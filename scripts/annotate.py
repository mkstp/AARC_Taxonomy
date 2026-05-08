"""
Gold annotation review session — turn-level AARC deficit labeling.

For each turn, displays the trailing 7-turn context alongside Claude's
pre-annotation (if available), then prompts to accept or override.

Usage:
    python3 scripts/annotate.py                              # annotate all turns
    python3 scripts/annotate.py --list                       # show progress and exit
    python3 scripts/annotate.py --dialogues scenario-001,scenario-003
    python3 scripts/annotate.py --corpus PATH --output PATH
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from fpo_mediation.corpus_manager import load_all
from fpo_mediation.gold_annotation_reviewer import load_turn_annotations, run_review_session
from fpo_mediation.persona_scenario_library import load_personas, load_scenarios
from fpo_mediation.claude_annotator import load_pre_annotations

CORPUS = str(ROOT / "data" / "corpus.jsonl")
PERSONAS = str(ROOT / "data" / "personas.json")
SCENARIOS = str(ROOT / "data" / "scenarios.json")
TURN_ANNOTATIONS = str(ROOT / "data" / "gold_annotations.jsonl")
PRE_ANNOTATIONS = str(ROOT / "data" / "pre_annotations.jsonl")


def show_progress(
    transcripts: list,
    annotations_path: str,
    pre_annotations_path: str,
    scenario_filter: set[str] | None,
    scenario_map: dict[str, str],
    pre_annotated_only: bool = False,
) -> None:
    if scenario_filter:
        transcripts = [t for t in transcripts if t["scenario_id"] in scenario_filter]

    annotated = {a["turn_id"] for a in load_turn_annotations(annotations_path)}
    pre_annotated = {a["turn_id"] for a in load_pre_annotations(pre_annotations_path)}

    total_turns = sum(len(t["turns"]) for t in transcripts)
    done = sum(
        1 for t in transcripts
        for turn in t["turns"]
        if f"{t['id'][:8]}-t{turn['turn_index']:04d}" in annotated
    )
    has_pre = sum(
        1 for t in transcripts
        for turn in t["turns"]
        if f"{t['id'][:8]}-t{turn['turn_index']:04d}" in pre_annotated
    )
    if pre_annotated_only:
        remaining = has_pre - done
    else:
        remaining = total_turns - done

    print(f"\nScope:         {len(transcripts)} dialogue(s), {total_turns} turns")
    print(f"Annotated:     {done}")
    print(f"Pre-annotated: {has_pre}  (available to review)")
    print(f"Remaining:     {remaining}")

    if done > 0:
        turn_anns = [
            a for a in load_turn_annotations(annotations_path)
            if any(
                a["transcript_id"] == t["id"]
                for t in transcripts
            )
        ]
        deficit_counts = {c: 0 for c in ["acknowledgement", "agency", "reciprocity", "clarity"]}
        for a in turn_anns:
            for c in deficit_counts:
                if a.get(f"{c}_deficit"):
                    deficit_counts[c] += 1
        print(f"\nDeficit rates (gold-annotated turns):")
        for c, count in deficit_counts.items():
            pct = count / done * 100
            print(f"  {c.capitalize():<16} {count}/{done}  ({pct:.0f}%)")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(description="Turn-level gold annotation session.")
    parser.add_argument("--corpus", default=CORPUS)
    parser.add_argument("--output", default=TURN_ANNOTATIONS)
    parser.add_argument("--pre-annotations", default=PRE_ANNOTATIONS)
    parser.add_argument(
        "--dialogues",
        help="Comma-separated scenario IDs to annotate (e.g. scenario-001,scenario-003)",
    )
    parser.add_argument("--list", action="store_true", help="Show progress and exit")
    parser.add_argument(
        "--pre-annotated-only",
        action="store_true",
        help="Only queue turns that have a Claude pre-annotation (skip manual-entry fallback)",
    )
    args = parser.parse_args()

    transcripts = load_all(args.corpus)
    if not transcripts:
        print("Corpus is empty. Generate dialogues first.")
        sys.exit(1)

    personas = load_personas(PERSONAS)
    scenarios = load_scenarios(SCENARIOS)
    persona_map = {p["id"]: p["name"] for p in personas}
    scenario_map = {s["id"]: s.get("title", s["id"]) for s in scenarios}

    scenario_filter = (
        set(args.dialogues.split(",")) if args.dialogues else None
    )

    if args.list:
        show_progress(transcripts, args.output, args.pre_annotations, scenario_filter, scenario_map, args.pre_annotated_only)
        return

    show_progress(transcripts, args.output, args.pre_annotations, scenario_filter, scenario_map, args.pre_annotated_only)

    try:
        run_review_session(
            transcripts,
            args.output,
            args.pre_annotations,
            persona_map=persona_map,
            scenario_map=scenario_map,
            scenario_filter=scenario_filter,
            pre_annotated_only=args.pre_annotated_only,
        )
    except (KeyboardInterrupt, EOFError):
        print("\n\nSession interrupted. Progress saved.")
        sys.exit(0)


if __name__ == "__main__":
    main()
