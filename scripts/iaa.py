"""
Inter-annotator agreement: human (gold) vs. LLM pre-annotations.
Computes Cohen's Kappa, observed agreement, positive rates, and
Krippendorff's Alpha per AARC component.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).parent.parent / "data"
REPORTS_DIR = Path(__file__).parent.parent / "docs" / "reports"

COMPONENTS = [
    "acknowledgement_deficit",
    "agency_deficit",
    "reciprocity_deficit",
    "clarity_deficit",
]

LABELS = {
    "acknowledgement_deficit": "Acknowledgement (A)",
    "agency_deficit": "Agency (G)",
    "reciprocity_deficit": "Reciprocity (R)",
    "clarity_deficit": "Clarity (C)",
}


def load_jsonl(path):
    with open(path) as f:
        return {r["turn_id"]: r for r in (json.loads(line) for line in f)}


def cohen_kappa(h, l):
    n = len(h)
    Po = sum(a == b for a, b in zip(h, l)) / n
    p_h = sum(h) / n
    p_l = sum(l) / n
    Pe = p_h * p_l + (1 - p_h) * (1 - p_l)
    if Pe == 1.0:
        return 1.0
    return (Po - Pe) / (1 - Pe)


def krippendorff_alpha(h, l):
    """Nominal Krippendorff's Alpha for binary labels, 2 annotators."""
    n = len(h)
    Do = sum(a != b for a, b in zip(h, l)) / n
    all_vals = h + l
    p = sum(all_vals) / len(all_vals)
    De = 2 * p * (1 - p)
    if De == 0:
        return 1.0
    return 1 - Do / De


def compute(human_anns, llm_anns, common_ids):
    results = {}
    ids = sorted(common_ids)
    for comp in COMPONENTS:
        h = [int(human_anns[tid][comp]) for tid in ids]
        l = [int(llm_anns[tid][comp]) for tid in ids]
        n = len(h)
        Po = sum(a == b for a, b in zip(h, l)) / n
        tp = sum(a == 1 and b == 1 for a, b in zip(h, l))
        fp = sum(a == 0 and b == 1 for a, b in zip(h, l))
        fn = sum(a == 1 and b == 0 for a, b in zip(h, l))
        tn = sum(a == 0 and b == 0 for a, b in zip(h, l))
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        results[comp] = {
            "n": n,
            "observed_agreement": round(Po, 4),
            "human_positive_rate": round(sum(h) / n, 4),
            "llm_positive_rate": round(sum(l) / n, 4),
            "cohen_kappa": round(cohen_kappa(h, l), 4),
            "krippendorff_alpha": round(krippendorff_alpha(h, l), 4),
            "tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1, 4),
        }
    return results


def interpret_kappa(k):
    if k < 0:
        return "worse than chance"
    elif k < 0.20:
        return "slight"
    elif k < 0.40:
        return "fair"
    elif k < 0.60:
        return "moderate"
    elif k < 0.80:
        return "substantial"
    else:
        return "almost perfect"


def render_analysis(results, n_matched, n_human, n_llm, *, schema="current", llm_name="claude-sonnet-4-6"):
    lines = []
    lines.append("# Inter-Annotator Agreement Analysis")
    lines.append(f"\n**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    lines.append(f"**Annotators:** Human (gold standard, Marc) vs. LLM ({llm_name})")
    lines.append(f"**Matched turns:** {n_matched} of {n_human} human-annotated turns ({n_llm} LLM pre-annotations available)")
    lines.append(f"**Schema:** {schema}")
    lines.append(f"**Labels:** Binary deficit flags per AARC component (Acknowledgement, Agency, Reciprocity, Clarity)")
    lines.append(f"**Metrics:** Cohen's Kappa (κ), Krippendorff's Alpha (α), observed agreement (P_o), and per-annotator positive rates")

    lines.append("\n---\n")
    lines.append("## Results by Component\n")
    lines.append("| Component | κ | Interpretation | α | P_o | Human+ | LLM+ |")
    lines.append("|-----------|---|----------------|---|-----|--------|------|")
    for comp in COMPONENTS:
        r = results[comp]
        label = LABELS[comp]
        interp = interpret_kappa(r["cohen_kappa"])
        lines.append(
            f"| {label} "
            f"| {r['cohen_kappa']:.3f} | {interp} "
            f"| {r['krippendorff_alpha']:.3f} "
            f"| {r['observed_agreement']:.1%} "
            f"| {r['human_positive_rate']:.1%} "
            f"| {r['llm_positive_rate']:.1%} |"
        )

    lines.append("\n---\n")
    lines.append("## Positive Signal (F1 Analysis)\n")
    lines.append("Human annotations treated as ground truth. LLM as predictor.\n")
    lines.append("| Component | TP | FP | FN | TN | Precision | Recall | F1 |")
    lines.append("|-----------|----|----|----|----|-----------|--------|----|")
    total_tp = total_fp = total_fn = total_tn = 0
    for comp in COMPONENTS:
        r = results[comp]
        lines.append(
            f"| {LABELS[comp]} "
            f"| {r['tp']} | {r['fp']} | {r['fn']} | {r['tn']} "
            f"| {r['precision']:.3f} | {r['recall']:.3f} | {r['f1']:.3f} |"
        )
        total_tp += r['tp']; total_fp += r['fp']
        total_fn += r['fn']; total_tn += r['tn']
    macro_prec = sum(results[c]['precision'] for c in COMPONENTS) / len(COMPONENTS)
    macro_rec  = sum(results[c]['recall']    for c in COMPONENTS) / len(COMPONENTS)
    macro_f1   = sum(results[c]['f1']        for c in COMPONENTS) / len(COMPONENTS)
    lines.append(
        f"| **Macro avg** | | | | | "
        f"**{macro_prec:.3f}** | **{macro_rec:.3f}** | **{macro_f1:.3f}** |"
    )
    total_pos = total_tp + total_fn
    total_slots = n_matched * len(COMPONENTS)
    lines.append(
        f"\nTotal positive label slots (human): {total_pos} / {total_slots} "
        f"({total_pos / total_slots:.1%} positive rate). "
        f"Agreed positives (TP): {total_tp}. Agreed negatives (TN): {total_tn}."
    )

    lines.append("\n---\n")
    lines.append("## Analysis\n")

    # Prevalence check
    low_prevalence = [c for c in COMPONENTS if results[c]["human_positive_rate"] < 0.10]
    high_prevalence = [c for c in COMPONENTS if results[c]["human_positive_rate"] >= 0.10]

    lines.append("### Prevalence and Kappa Interpretation\n")
    if low_prevalence:
        lp_labels = ", ".join(LABELS[c] for c in low_prevalence)
        lines.append(
            f"The following components have a human positive rate below 10%: **{lp_labels}**. "
            f"For these components, kappa is subject to the prevalence paradox: even high observed "
            f"agreement produces a low kappa when one category dominates. Krippendorff's Alpha and "
            f"observed agreement should be weighted more heavily in interpretation."
        )
    if high_prevalence:
        hp_labels = ", ".join(LABELS[c] for c in high_prevalence)
        lines.append(
            f"\nThe following components have sufficient positive-case prevalence (≥ 10%) for "
            f"kappa to be straightforwardly interpretable: **{hp_labels}**."
        )

    lines.append("\n### Component-Level Findings\n")
    for comp in COMPONENTS:
        r = results[comp]
        label = LABELS[comp]
        kappa_str = f"κ = {r['cohen_kappa']:.3f} ({interpret_kappa(r['cohen_kappa'])})"
        alpha_str = f"α = {r['krippendorff_alpha']:.3f}"
        po_str = f"P_o = {r['observed_agreement']:.1%}"

        bias = r["llm_positive_rate"] - r["human_positive_rate"]
        if abs(bias) < 0.03:
            bias_note = "LLM and human positive rates are closely aligned."
        elif bias > 0:
            bias_note = f"LLM labels positive more often than the human annotator by {bias:.1%}, suggesting the model may be over-sensitive to this deficit."
        else:
            bias_note = f"LLM labels positive less often than the human annotator by {abs(bias):.1%}, suggesting the model may be under-sensitive to this deficit."

        lines.append(f"**{label}:** {kappa_str}, {alpha_str}, {po_str}. {bias_note}\n")

    lines.append("### Overall Assessment\n")
    mean_kappa = sum(results[c]["cohen_kappa"] for c in COMPONENTS) / len(COMPONENTS)
    mean_alpha = sum(results[c]["krippendorff_alpha"] for c in COMPONENTS) / len(COMPONENTS)
    mean_po = sum(results[c]["observed_agreement"] for c in COMPONENTS) / len(COMPONENTS)
    lines.append(
        f"Mean across components: κ = {mean_kappa:.3f}, α = {mean_alpha:.3f}, P_o = {mean_po:.1%}. "
        f"These figures reflect agreement under the {schema} schema. They should not be used as a "
        f"final validity measure for the corpus; they establish a reference point for tracking "
        f"annotation quality across schema iterations."
    )

    lines.append("\n### Limitations\n")
    lines.append(
        f"1. **Schema version:** All {n_matched} turns were annotated under the {schema} schema.\n"
        f"2. **Sample size:** {n_matched} turns from a single corpus provides adequate signal "
        "for per-component trending but is underpowered for fine-grained subcategory analysis.\n"
        "3. **LLM annotator:** The LLM was prompted to apply the schema; any systematic "
        "prompt-induced bias (e.g., conservative labeling under the opening-turn epistemic "
        "constraint) will suppress positive rates and inflate apparent agreement on negatives."
    )

    return "\n".join(lines)


def print_summary(results: dict) -> None:
    """Print the per-component kappa/F1 table to stdout."""
    print(f"\n{'Component':<28} {'κ':>7} {'α':>7} {'P_o':>7} {'H+':>6} {'LLM+':>6} {'F1':>6}")
    print("-" * 73)
    for comp in COMPONENTS:
        r = results[comp]
        print(
            f"{LABELS[comp]:<28} "
            f"{r['cohen_kappa']:>7.3f} "
            f"{r['krippendorff_alpha']:>7.3f} "
            f"{r['observed_agreement']:>7.1%} "
            f"{r['human_positive_rate']:>6.1%} "
            f"{r['llm_positive_rate']:>6.1%} "
            f"{r['f1']:>6.3f}"
        )
    mean_kappa = sum(results[c]["cohen_kappa"] for c in COMPONENTS) / len(COMPONENTS)
    mean_alpha = sum(results[c]["krippendorff_alpha"] for c in COMPONENTS) / len(COMPONENTS)
    mean_po    = sum(results[c]["observed_agreement"] for c in COMPONENTS) / len(COMPONENTS)
    mean_f1    = sum(results[c]["f1"]                 for c in COMPONENTS) / len(COMPONENTS)
    print("-" * 73)
    print(f"{'Mean':<28} {mean_kappa:>7.3f} {mean_alpha:>7.3f} {mean_po:>7.1%} {'':>6} {'':>6} {mean_f1:>6.3f}")


def main():
    import argparse
    default_filename = f"iaa_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.md"
    parser = argparse.ArgumentParser(description="Inter-annotator agreement analysis.")
    parser.add_argument(
        "--human",
        default=str(DATA_DIR / "gold_annotations.jsonl"),
        help="Path to human (gold) annotations JSONL",
    )
    parser.add_argument(
        "--llm",
        default=str(DATA_DIR / "pre_annotations.jsonl"),
        help="Path to LLM annotations JSONL",
    )
    parser.add_argument(
        "--output",
        default=default_filename,
        help=f"Output filename within docs/reports/ (default: {default_filename})",
    )
    parser.add_argument(
        "--no-report",
        action="store_true",
        help="Print stats to stdout only; do not write a markdown report",
    )
    parser.add_argument(
        "--schema",
        default="current",
        help="Schema version label to embed in the report (default: current)",
    )
    parser.add_argument(
        "--llm-name",
        default="claude-sonnet-4-6",
        dest="llm_name",
        help="Name of the LLM annotator to embed in the report (default: claude-sonnet-4-6)",
    )
    args = parser.parse_args()

    human_anns = load_jsonl(args.human)
    llm_anns   = load_jsonl(args.llm)

    common_ids = set(human_anns) & set(llm_anns)
    print(f"Human annotations: {len(human_anns)}")
    print(f"LLM annotations:   {len(llm_anns)}")
    print(f"Matched turns:     {len(common_ids)}")

    results = compute(human_anns, llm_anns, common_ids)
    print_summary(results)

    if args.no_report:
        return

    out_path = REPORTS_DIR / args.output
    if out_path.exists():
        print(f"\nERROR: {out_path} already exists. Use --output to specify a different filename.")
        raise SystemExit(1)

    analysis = render_analysis(results, len(common_ids), len(human_anns), len(llm_anns), schema=args.schema, llm_name=args.llm_name)
    out_path.write_text(analysis)
    print(f"\nAnalysis written to {out_path}")


if __name__ == "__main__":
    main()
