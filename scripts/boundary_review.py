"""
Compile boundary-flagged turns into a review document.

Finds all turns in gold_annotations.jsonl where boundary_case=True, then
produces a markdown document showing: the trailing 7-turn context window,
human labels, LLM pre-annotation labels + rationale, and any disagreements.

Usage:
    python3 scripts/boundary_review.py
    python3 scripts/boundary_review.py --output docs/reports/boundary_review.md
    python3 scripts/boundary_review.py --component clarity  # filter by component
"""

import argparse
import json
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent.parent

CORPUS = ROOT / "data" / "corpus.jsonl"
TURN_ANNOTATIONS = ROOT / "data" / "gold_annotations.jsonl"
PRE_ANNOTATIONS = ROOT / "data" / "pre_annotations.jsonl"
DEFAULT_OUTPUT = ROOT / "docs" / "reports" / "boundary_review.md"

COMPONENTS = ["acknowledgement", "agency", "reciprocity", "clarity"]
LABELS = {"acknowledgement": "A", "agency": "G", "reciprocity": "R", "clarity": "C"}


def load_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def build_corpus_index(records: list[dict]) -> dict[str, dict]:
    return {r["turn_id"]: r for r in records}


def get_context_window(corpus_index: dict, transcript_id: str, turn_index: int, window: int = 6) -> list[dict]:
    prefix = transcript_id[:8]
    turns = []
    for i in range(max(0, turn_index - window), turn_index + 1):
        tid = f"{prefix}-t{i:04d}"
        if tid in corpus_index:
            turns.append(corpus_index[tid])
    return turns


def label_str(ann: dict) -> str:
    parts = []
    for comp in COMPONENTS:
        key = f"{comp}_deficit"
        val = ann.get(key)
        parts.append(f"{LABELS[comp]}:{'Y' if val else 'N'}")
    return "  ".join(parts)


def disagreements(human: dict, llm: dict) -> list[str]:
    return [
        LABELS[comp]
        for comp in COMPONENTS
        if human.get(f"{comp}_deficit") != llm.get(f"{comp}_deficit")
    ]


def render(flagged: list[dict], human_map: dict, llm_map: dict, corpus_index: dict, component_filter: str | None) -> str:
    lines = []
    lines.append("# Boundary Case Review")
    lines.append(f"\n**Generated:** {date.today().isoformat()}")
    lines.append(f"**Flagged turns:** {len(flagged)}")
    if component_filter:
        lines.append(f"**Filter:** {component_filter.capitalize()} only")
    lines.append("\n---\n")

    for i, ann in enumerate(flagged, 1):
        tid = ann["turn_id"]
        llm = llm_map.get(tid)
        disagree = disagreements(ann, llm) if llm else []

        lines.append(f"## [{i}] Turn `{tid}`")
        lines.append(f"*Transcript:* `{ann['transcript_id'][:8]}` · *Turn index:* {ann['turn_index']} · *Annotated:* {ann.get('annotation_date', '?')}")
        if ann.get("annotator_notes"):
            lines.append(f"*Annotator note:* {ann['annotator_notes']}")
        lines.append("")

        # Context window
        lines.append("### Context window\n")
        context = get_context_window(corpus_index, ann["transcript_id"], ann["turn_index"])
        for turn in context:
            marker = "►" if turn["turn_index"] == ann["turn_index"] else " "
            speaker = turn.get("speaker", "?").replace("party_", "").upper()
            lines.append(f"    {marker} [{turn['turn_index']:2d}]  {speaker}: {turn.get('text', '')}")
        lines.append("")

        # Labels
        lines.append("### Labels\n")
        lines.append(f"| Annotator | {' | '.join(LABELS[c] for c in COMPONENTS)} | Notes |")
        lines.append("|-----------|" + "|".join("---" for _ in COMPONENTS) + "|-------|")

        human_vals = " | ".join("**Y**" if ann.get(f"{c}_deficit") else "N" for c in COMPONENTS)
        lines.append(f"| Human | {human_vals} | {ann.get('annotator_notes', '')} |")

        if llm:
            llm_vals = " | ".join("**Y**" if llm.get(f"{c}_deficit") else "N" for c in COMPONENTS)
            lines.append(f"| LLM | {llm_vals} | {llm.get('rationale', '')} |")
        else:
            lines.append("| LLM | — | — | — | — | *(no pre-annotation)* |")

        if disagree:
            lines.append(f"\n**Disagreements:** {', '.join(disagree)}")

        lines.append("\n---\n")

    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Compile boundary-flagged turns for review.")
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    parser.add_argument("--component", help="Filter to turns with a boundary flag on a specific component (acknowledgement|agency|reciprocity|clarity)")
    args = parser.parse_args()

    human_anns = load_jsonl(TURN_ANNOTATIONS)
    llm_anns = load_jsonl(PRE_ANNOTATIONS)
    corpus = load_jsonl(CORPUS)

    # Build turn-level corpus index from flat turn records
    corpus_index: dict[str, dict] = {}
    for transcript in corpus:
        prefix = transcript["id"][:8]
        for turn in transcript.get("turns", []):
            tid = f"{prefix}-t{turn['turn_index']:04d}"
            corpus_index[tid] = {**turn, "transcript_id": transcript["id"]}

    llm_map = {r["turn_id"]: r for r in llm_anns}
    human_map = {r["turn_id"]: r for r in human_anns}

    flagged = [r for r in human_anns if r.get("boundary_case")]

    if args.component:
        comp = args.component.lower()
        if comp not in COMPONENTS:
            print(f"Unknown component '{comp}'. Choose from: {', '.join(COMPONENTS)}")
            raise SystemExit(1)
        flagged = [r for r in flagged if r.get(f"{comp}_deficit") or llm_map.get(r["turn_id"], {}).get(f"{comp}_deficit")]

    if not flagged:
        print("No boundary-flagged turns found.")
        return

    print(f"Found {len(flagged)} boundary-flagged turn(s).")

    doc = render(flagged, human_map, llm_map, corpus_index, args.component)
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(doc, encoding="utf-8")
    print(f"Review document written to {out}")


if __name__ == "__main__":
    main()
