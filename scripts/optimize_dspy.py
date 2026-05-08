"""
MiPROv2 optimization for AARC turn annotation.

Compiles an AARCAnnotator DSPy program against the 140-turn gold set using a
recall-weighted metric: tp=1.0, tn=0.3, fp/fn=0.0. This penalises all-False
strategies on low-prevalence labels (Clarity 15.7%) without ignoring true negatives.

Each run saves to a timestamped file (data/dspy_program_YYYYMMDD_HHMMSS.json)
so prior programs are never overwritten. Pass the saved path to silver_annotate
via --program-path.

Usage:
    python3 scripts/optimize_dspy.py                       # light run, gpt-5.4
    python3 scripts/optimize_dspy.py --auto medium
    python3 scripts/optimize_dspy.py --eval-only --program data/dspy_program_<ts>.json
"""

import argparse
import json
import random
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

import dspy
from fpo_mediation.corpus_manager import load_all
from fpo_mediation.gold_annotation_reviewer import load_turn_annotations
from fpo_mediation.claude_annotator import format_context
from fpo_mediation.dspy_annotator import AARCAnnotator, LABELS

CORPUS = str(ROOT / "data" / "corpus.jsonl")
GOLD = str(ROOT / "data" / "gold_annotations.jsonl")


def build_examples(transcripts: list, gold: list) -> list[dspy.Example]:
    transcript_map = {t["id"]: t for t in transcripts}
    examples = []
    for ann in gold:
        transcript = transcript_map.get(ann["transcript_id"])
        if transcript is None:
            continue
        context = format_context(transcript, ann["turn_index"])
        ex = dspy.Example(
            dialogue_context=context,
            acknowledgement_deficit=ann["acknowledgement_deficit"],
            agency_deficit=ann["agency_deficit"],
            reciprocity_deficit=ann["reciprocity_deficit"],
            clarity_deficit=ann["clarity_deficit"],
        ).with_inputs("dialogue_context")
        examples.append(ex)
    return examples


def recall_weighted_metric(example, pred, trace=None) -> float:
    """tp=1.0, tn=0.3, fp=0.0, fn=0.0 — penalises all-False on low-prevalence labels.

    For a 15%-positive label (e.g. Clarity), always-False scores 0.255 per label;
    detecting even half the positives correctly scores ~0.38. This prevents the
    optimizer from suppressing rare labels to game per-example accuracy.
    """
    score = 0.0
    for label in LABELS:
        gold = bool(example[label])
        pred_val = bool(getattr(pred, label, False))
        if gold and pred_val:
            score += 1.0
        elif not gold and not pred_val:
            score += 0.3
    return score / len(LABELS)


def f1_report(examples: list, preds: list) -> dict:
    """Compute per-label F1 and macro-F1 over a set of examples."""
    report = {}
    for label in LABELS:
        tp = fp = fn = 0
        for ex, pred in zip(examples, preds):
            gold_val = bool(ex[label])
            pred_val = bool(getattr(pred, label, False))
            if gold_val and pred_val:
                tp += 1
            elif not gold_val and pred_val:
                fp += 1
            elif gold_val and not pred_val:
                fn += 1
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
        report[label] = {"precision": precision, "recall": recall, "f1": f1, "tp": tp, "fp": fp, "fn": fn}
    macro_f1 = sum(v["f1"] for v in report.values()) / len(LABELS)
    report["macro_f1"] = macro_f1
    return report


def evaluate(program: dspy.Module, examples: list) -> tuple[list, dict]:
    preds = [program(dialogue_context=ex.dialogue_context) for ex in examples]
    return preds, f1_report(examples, preds)


def print_report(report: dict, label: str = "") -> None:
    header = f"  {label}" if label else ""
    if header:
        print(header)
    short = {"acknowledgement_deficit": "Ack", "agency_deficit": "Aga", "reciprocity_deficit": "Rec", "clarity_deficit": "Cla"}
    for l in LABELS:
        r = report[l]
        print(f"    {short[l]}:  P={r['precision']:.3f}  R={r['recall']:.3f}  F1={r['f1']:.3f}  (tp={r['tp']} fp={r['fp']} fn={r['fn']})")
    print(f"    Macro-F1: {report['macro_f1']:.3f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="MiPROv2 optimization for AARC annotation.")
    parser.add_argument("--model", default="openai/gpt-5.4",
                        help="LiteLLM model string for both prompt and task model")
    parser.add_argument("--auto", default="light", choices=["light", "medium", "heavy"],
                        help="MiPROv2 search budget")
    parser.add_argument("--max-labeled-demos", type=int, default=2)
    parser.add_argument("--max-bootstrapped-demos", type=int, default=2)
    parser.add_argument("--val-size", type=int, default=40,
                        help="Number of gold examples held out for validation")
    parser.add_argument("--seed", type=int, default=42)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    parser.add_argument("--output", default=str(ROOT / "data" / f"dspy_program_{ts}.json"))
    parser.add_argument("--eval-only", action="store_true",
                        help="Skip optimization; evaluate the saved program on val set")
    args = parser.parse_args()

    transcripts = load_all(CORPUS)
    gold = load_turn_annotations(GOLD)

    examples = build_examples(transcripts, gold)
    print(f"Loaded {len(examples)} gold examples")

    random.seed(args.seed)
    random.shuffle(examples)
    val = examples[:args.val_size]
    train = examples[args.val_size:]
    print(f"Train: {len(train)}, Val: {len(val)}")

    task_lm = dspy.LM(args.model, max_tokens=128, temperature=0.0)
    prompt_lm = dspy.LM(args.model, max_tokens=2048, temperature=0.7)
    dspy.configure(lm=task_lm)

    if args.eval_only:
        program = AARCAnnotator()
        program.load(args.output)
        print(f"\nLoaded program from {args.output}")
        print("\nVal-set evaluation:")
        _, report = evaluate(program, val)
        print_report(report, "val")
        return

    # Baseline: unoptimized program on val
    print("\nBaseline (unoptimized) val evaluation:")
    baseline_program = AARCAnnotator()
    _, baseline_report = evaluate(baseline_program, val)
    print_report(baseline_report)

    # Optimize
    print(f"\nRunning MiPROv2 (auto={args.auto}, labeled_demos={args.max_labeled_demos}, bootstrap_demos={args.max_bootstrapped_demos}) ...")
    optimizer = dspy.MIPROv2(
        metric=recall_weighted_metric,
        prompt_model=prompt_lm,
        task_model=task_lm,
        auto=args.auto,
        max_labeled_demos=args.max_labeled_demos,
        max_bootstrapped_demos=args.max_bootstrapped_demos,
        verbose=True,
    )
    optimized = optimizer.compile(baseline_program, trainset=train, valset=val)

    # Save
    optimized.save(args.output)
    print(f"\nSaved optimized program to {args.output}")

    # Evaluate optimized program
    print("\nOptimized program val evaluation:")
    _, opt_report = evaluate(optimized, val)
    print_report(opt_report)

    # Delta
    print(f"\nMacro-F1 delta: {opt_report['macro_f1'] - baseline_report['macro_f1']:+.3f}")


if __name__ == "__main__":
    main()
