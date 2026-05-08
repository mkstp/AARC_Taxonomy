"""
Full-corpus silver annotation pass.

Annotates turns using a streamlined tool (four boolean deficit labels only —
no rationale, no confidence). Results are saved to silver_annotations.jsonl as
TurnAnnotation records. By default, turns already covered by gold_annotations.jsonl
are skipped.

Provider selection:
    --provider claude   Claude Sonnet-4-6 via Anthropic API (default)
    --provider gpt      OpenAI-compatible model via OpenAI API
    --provider groq     Groq-hosted model via Groq API (default: qwen/qwen3-32b)
    --provider dspy     DSPy MiPROv2-optimized program (requires data/dspy_program.json)
    --provider dspy-ara DSPy AGR-only program — A/G/R labels, Clarity excluded (requires data/dspy_program_ara.json)

Usage:
    python3 scripts/silver_annotate.py                              # annotate all remaining turns (claude)
    python3 scripts/silver_annotate.py --list                       # show progress and exit
    python3 scripts/silver_annotate.py --batch-size 100             # annotate at most 100 turns
    python3 scripts/silver_annotate.py --provider gpt --model <id> --output data/gpt_annotations.jsonl --gold-only
"""

import argparse
import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

from dotenv import load_dotenv
load_dotenv(ROOT / ".env")
sys.path.insert(0, str(ROOT / "src"))

from fpo_mediation.corpus_manager import load_all
from fpo_mediation.gold_annotation_reviewer import load_turn_annotations
from fpo_mediation.claude_annotator import load_silver_annotations

CORPUS = str(ROOT / "data" / "corpus.jsonl")
GOLD_ANNOTATIONS = str(ROOT / "data" / "gold_annotations.jsonl")
SILVER_ANNOTATIONS = str(ROOT / "data" / "silver_annotations.jsonl")
TAXONOMY = str(ROOT / "docs" / "aarc_taxonomy.md")

_DEFAULT_MODELS = {
    "claude": "claude-sonnet-4-6",
    "gpt": None,  # must be specified explicitly
    "groq": "qwen/qwen3-32b",
    "dspy": "openai/gpt-5.4",
    "dspy-ara": "openai/gpt-5.4",
}


def show_progress(transcripts: list, gold_path: str, silver_path: str) -> None:
    gold = load_turn_annotations(gold_path)
    silver = load_silver_annotations(silver_path)
    annotated_ids = {a["turn_id"] for a in gold} | {a["turn_id"] for a in silver}
    total = sum(len(t["turns"]) for t in transcripts)
    print(f"\nCorpus:    {len(transcripts)} dialogues, {total} turns")
    print(f"Gold:      {len(gold)}")
    print(f"Silver:    {len(silver)}")
    print(f"Remaining: {total - len(annotated_ids)}")
    print()


async def main() -> None:
    parser = argparse.ArgumentParser(description="Full-corpus silver annotation pass.")
    parser.add_argument("--provider", default="claude", choices=["claude", "gpt", "groq", "dspy", "dspy-ara"],
                        help="Annotation provider: 'claude' (default), 'gpt', 'groq', or 'dspy'")
    parser.add_argument("--corpus", default=CORPUS)
    parser.add_argument("--gold", default=GOLD_ANNOTATIONS)
    parser.add_argument("--output", default=SILVER_ANNOTATIONS)
    parser.add_argument("--taxonomy", default=TAXONOMY)
    parser.add_argument("--model", default=None,
                        help="Model ID (default: claude-sonnet-4-6 for claude; required for gpt)")
    parser.add_argument("--batch-size", type=int, default=None,
                        help="Annotate at most N turns (default: all remaining)")
    parser.add_argument("--include-gold", action="store_true",
                        help="Do not skip gold-annotated turns (annotates full corpus including gold)")
    parser.add_argument("--gold-only", action="store_true",
                        help="Annotate only the turns present in the gold file (for IAA comparison runs)")
    parser.add_argument("--list", action="store_true", help="Show progress and exit")
    parser.add_argument("--program-path", default=None,
                        help="Path to compiled DSPy program JSON (--provider dspy only)")
    args = parser.parse_args()

    if args.provider == "gpt" and args.model is None:
        print("Error: --model is required when using --provider gpt", file=sys.stderr)
        sys.exit(1)

    model = args.model or _DEFAULT_MODELS[args.provider]

    transcripts = load_all(args.corpus)
    if not transcripts:
        print("Corpus is empty.")
        sys.exit(1)

    show_progress(transcripts, args.gold, args.output)

    if args.list:
        return

    gold_annotations = load_turn_annotations(args.gold)
    gold_ids: set[str] = set()
    if not args.include_gold and not args.gold_only:
        gold_ids = {a["turn_id"] for a in gold_annotations}

    if args.gold_only:
        # Restrict pending turns to only those present in the gold file
        gold_turn_ids = {a["turn_id"] for a in gold_annotations}
        for transcript in transcripts:
            transcript["turns"] = [
                t for t in transcript["turns"]
                if f"{transcript['id'][:8]}-t{t['turn_index']:04d}" in gold_turn_ids
            ]

    total_turns = sum(len(t["turns"]) for t in transcripts)
    batch_size = args.batch_size or total_turns

    if args.provider == "claude":
        from anthropic import AsyncAnthropic
        from fpo_mediation.claude_annotator import silverannotate_batch
        client = AsyncAnthropic()
    elif args.provider == "gpt":
        from openai import AsyncOpenAI
        from fpo_mediation.gpt_annotator import silverannotate_batch
        client = AsyncOpenAI()
    elif args.provider == "groq":
        from fpo_mediation.groq_annotator import silverannotate_batch, make_groq_client
        client = make_groq_client()
    elif args.provider == "dspy-ara":
        from fpo_mediation.dspy_annotator_ara import silverannotate_batch
        client = None
    else:
        from fpo_mediation.dspy_annotator import silverannotate_batch
        client = None

    extra_kwargs = {}
    if args.provider in ("dspy", "dspy-ara") and args.program_path:
        extra_kwargs["program_path"] = args.program_path

    count = await silverannotate_batch(
        transcripts=transcripts,
        taxonomy_path=args.taxonomy,
        output_path=args.output,
        batch_size=batch_size,
        client=client,
        skip_ids=gold_ids,
        model=model,
        **extra_kwargs,
    )

    if count == 0:
        print("All turns already annotated.")
    else:
        print(f"\nDone. {count} annotations written to {Path(args.output).name}")


if __name__ == "__main__":
    asyncio.run(main())
