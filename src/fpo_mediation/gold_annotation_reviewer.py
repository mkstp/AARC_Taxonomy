"""MOD-005: GoldAnnotationReviewer — Implements DEL-005. Validated by VC-02, VC-04."""

import json
from datetime import date
from pathlib import Path

from .models import DialogueWindow, GoldAnnotation, PreAnnotation, Transcript, TurnAnnotation
from .claude_annotator import load_pre_annotations, make_turn_id

_COMPONENTS = ["acknowledgement", "agency", "reciprocity", "clarity"]
_COMPONENT_KEYS = ["a", "g", "r", "c"]
_HELP = (
    "  [Enter]   accept Claude's labels as-is\n"
    "  [a/g/r/c] flip individual labels (combine: 'ar' flips A and R)\n"
    "  [n]       add annotator note (combine with flips: 'gn' flips G and adds note)\n"
    "  [b]       flag as boundary case for review (combine with others: 'cb' flips C and flags)\n"
    "  [s]       skip this turn\n"
    "  [?]       show this help\n"
    "  Ctrl+C    save progress and exit\n"
    "\n"
    "  Confidence prompt: 1=low  2=medium  3=high  Enter=3 (default)\n"
)


# ---------------------------------------------------------------------------
# Window-level functions — kept for backward compatibility with existing tests
# ---------------------------------------------------------------------------

def display_window(window: DialogueWindow) -> None:
    print(f"\n{'=' * 60}")
    print(
        f"Window {window['id']}  "
        f"(transcript: {window['transcript_id']}, index: {window['window_index']})"
    )
    print(f"{'=' * 60}")
    for turn in window["turns"]:
        speaker = turn["speaker"].upper()
        print(f"  [{turn['turn_index']}] {speaker}: {turn['text']}")
        note = turn.get("director_note", "")
        if note:
            print(f"       [director: {note}]")
    print()


def prompt_labels() -> dict:
    labels = {}
    for component in _COMPONENTS:
        while True:
            raw = input(f"  {component.capitalize()} deficit? (y/n): ").strip().lower()
            if raw in ("y", "n"):
                labels[f"{component}_deficit"] = raw == "y"
                break
            print("  Please enter 'y' or 'n'.")
    return labels


def save_annotation(annotation: GoldAnnotation, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(annotation) + "\n")


def load_annotations(path: str) -> list[GoldAnnotation]:
    p = Path(path)
    if not p.exists():
        return []
    annotations = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                annotations.append(json.loads(line))
    return annotations


# ---------------------------------------------------------------------------
# Turn-level functions
# ---------------------------------------------------------------------------

def save_turn_annotation(annotation: TurnAnnotation, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(annotation) + "\n")


def load_turn_annotations(path: str) -> list[TurnAnnotation]:
    p = Path(path)
    if not p.exists():
        return []
    annotations = []
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                annotations.append(json.loads(line))
    return annotations


def display_turn_in_context(
    transcript: Transcript,
    turn_index: int,
    *,
    name_a: str = "Party A",
    name_b: str = "Party B",
    scenario_title: str | None = None,
) -> None:
    turns = transcript["turns"]
    start = max(0, turn_index - 6)
    context = turns[start : turn_index + 1]

    focal_turn = next(t for t in turns if t["turn_index"] == turn_index)
    focal_speaker = name_a if focal_turn["speaker"] == "party_a" else name_b

    title = scenario_title or transcript["scenario_id"]
    print(f"\n  {'─' * 66}")
    print(
        f"  Turn {turn_index} of {len(turns) - 1}  ·  {title}  ·  "
        f"Speaker: {focal_speaker}"
    )
    print(f"  {'─' * 66}")
    for turn in context:
        speaker = name_a if turn["speaker"] == "party_a" else name_b
        marker = "►" if turn["turn_index"] == turn_index else " "
        print(f"  {marker}  [{turn['turn_index']:2d}]  {speaker}: {turn['text']}")
    print()


def _format_labels(pre: PreAnnotation) -> str:
    return (
        f"  A:{'Y' if pre['acknowledgement_deficit'] else 'N'}  "
        f"Ag:{'Y' if pre['agency_deficit'] else 'N'}  "
        f"R:{'Y' if pre['reciprocity_deficit'] else 'N'}  "
        f"C:{'Y' if pre['clarity_deficit'] else 'N'}"
    )


def _prompt_with_suggestion(pre: PreAnnotation) -> dict | None:
    """
    Display Claude's suggestion and prompt for accept/flip/note/skip.
    Returns a labels dict, or None if skipped.
    """
    print(f"  Claude ({pre['confidence']:.2f}):{_format_labels(pre)}")
    print(f"  \"{pre['rationale']}\"")
    print()

    labels = {
        "acknowledgement_deficit": pre["acknowledgement_deficit"],
        "agency_deficit": pre["agency_deficit"],
        "reciprocity_deficit": pre["reciprocity_deficit"],
        "clarity_deficit": pre["clarity_deficit"],
    }
    notes = ""
    boundary = False

    while True:
        raw = input("  [Enter]=accept · [a/g/r/c]=flip · [n]otes · [b]oundary · [s]kip · [?]help\n  > ").strip().lower()

        if raw == "?":
            print(_HELP)
            continue
        if raw == "s":
            return None

        # flip any combination of a/g/r/c
        for char, component in zip(_COMPONENT_KEYS, _COMPONENTS):
            if char in raw:
                labels[f"{component}_deficit"] = not labels[f"{component}_deficit"]

        # re-display if any flips happened
        if any(c in raw for c in _COMPONENT_KEYS):
            flipped = [
                f"{'Y' if labels[f'{c}_deficit'] else 'N'}"
                for c in _COMPONENTS
            ]
            print(f"  Updated:  A:{flipped[0]}  Ag:{flipped[1]}  R:{flipped[2]}  C:{flipped[3]}")

        if "b" in raw:
            boundary = True
            print("  [Boundary case flagged]")

        if "n" in raw:
            notes = input("  Note: ").strip()

        conf_raw = input("  Confidence [1-3, Enter=3]: ").strip()
        confidence = int(conf_raw) if conf_raw in ("1", "2", "3") else 3

        labels["annotator_notes"] = notes
        labels["annotator_confidence"] = confidence
        labels["boundary_case"] = boundary
        return labels


def _prompt_manual() -> dict | None:
    """Fallback: no pre-annotation available. Returns labels dict or None if skipped."""
    print("  [No pre-annotation — entering manually]")
    raw = input("  [s]kip or press Enter to continue: ").strip().lower()
    if raw == "s":
        return None

    labels = {}
    boundary = False
    for component in _COMPONENTS:
        while True:
            val = input(f"  {component.capitalize()} deficit? (y/n/yb/nb): ").strip().lower()
            flagged = "b" in val
            if val.replace("b", "") in ("y", "n"):
                labels[f"{component}_deficit"] = "y" in val
                if flagged:
                    boundary = True
                    print("  [Boundary case flagged]")
                break
            print("  Please enter 'y', 'n', 'yb' (yes + boundary), or 'nb' (no + boundary).")
    notes = input("  Notes (optional): ").strip()
    conf_raw = input("  Confidence [1-3, Enter=3]: ").strip()
    confidence = int(conf_raw) if conf_raw in ("1", "2", "3") else 3
    labels["annotator_notes"] = notes
    labels["annotator_confidence"] = confidence
    labels["boundary_case"] = boundary
    return labels


def run_review_session(
    transcripts: list[Transcript],
    output_path: str,
    pre_annotations_path: str,
    *,
    persona_map: dict[str, str] | None = None,
    scenario_map: dict[str, str] | None = None,
    scenario_filter: set[str] | None = None,
    pre_annotated_only: bool = False,
) -> None:
    """
    Turn-level gold annotation session.

    Iterates over all turns in the selected transcripts. For each unannotated
    turn, displays the trailing 7-turn context and Claude's pre-annotation
    (if available), then prompts the annotator to accept or override.
    """
    existing = {a["turn_id"] for a in load_turn_annotations(output_path)}
    pre_map: dict[str, PreAnnotation] = {
        a["turn_id"]: a for a in load_pre_annotations(pre_annotations_path)
    }

    # Build pending list
    pending = []
    for transcript in transcripts:
        if scenario_filter and transcript["scenario_id"] not in scenario_filter:
            continue
        for turn in transcript["turns"]:
            tid = make_turn_id(transcript["id"], turn["turn_index"])
            if tid not in existing:
                if pre_annotated_only and tid not in pre_map:
                    continue
                pending.append((transcript, turn["turn_index"]))

    if not pending:
        print("All turns in the selected dialogues have been annotated.")
        return

    annotated_by = input("Annotator ID: ").strip() or "unknown"
    total = len(pending)
    print(f"\n{total} turn(s) to annotate. Ctrl+C to save and exit.\n")

    for i, (transcript, turn_index) in enumerate(pending, 1):
        name_a = persona_map.get(transcript["persona_a_id"], "Party A") if persona_map else "Party A"
        name_b = persona_map.get(transcript["persona_b_id"], "Party B") if persona_map else "Party B"
        title = scenario_map.get(transcript["scenario_id"]) if scenario_map else None

        print(f"[{i}/{total}]", end="")
        display_turn_in_context(
            transcript, turn_index, name_a=name_a, name_b=name_b, scenario_title=title
        )

        tid = make_turn_id(transcript["id"], turn_index)
        pre = pre_map.get(tid)

        labels = _prompt_with_suggestion(pre) if pre else _prompt_manual()

        if labels is None:
            print("  Skipped.\n")
            continue

        annotation: TurnAnnotation = {
            "turn_id": tid,
            "transcript_id": transcript["id"],
            "turn_index": turn_index,
            "acknowledgement_deficit": labels["acknowledgement_deficit"],
            "agency_deficit": labels["agency_deficit"],
            "reciprocity_deficit": labels["reciprocity_deficit"],
            "clarity_deficit": labels["clarity_deficit"],
            "annotator_notes": labels.get("annotator_notes", ""),
            "annotator_confidence": labels.get("annotator_confidence", 3),
            "boundary_case": labels.get("boundary_case", False),
            "annotated_by": annotated_by,
            "annotation_date": date.today().isoformat(),
        }
        save_turn_annotation(annotation, output_path)
        print(f"  Saved. ({total - i} remaining)\n")
