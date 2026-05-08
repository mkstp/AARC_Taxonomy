"""Silver-annotator: Claude-powered turn-level AARC deficit annotation."""

import json
from datetime import date
from pathlib import Path

from anthropic import AsyncAnthropic

from .models import PreAnnotation, TurnAnnotation, Transcript

_TASK_PREAMBLE = """\
You are an expert annotator for a mediation dialogue corpus. Your task is to \
label a single dialogue turn for AARC deficits using the taxonomy below.

"""

_TASK_INSTRUCTIONS = """
## Annotation task

You will be given a dialogue excerpt. The focal turn is marked ► and its \
speaker is identified at the top of the context block. Your task is to answer \
a single question about that turn: *what does this utterance demonstrate about \
the focal speaker's evolving needs?* Labels are speaker-attributed — they \
describe what the speaker is currently experiencing or exhibiting, not what is \
being done to them.

For each of the four components, indicate whether a deficit is present (true) \
or absent (false). Note:
- Apply the diagnostic priority ordering: Acknowledgement → Agency → \
Reciprocity → Clarity. Where a turn could fall under two components, assign \
it to the earlier one.
- The unit of evidence is the trailing window, not the turn in isolation. Use \
the preceding turns as accumulating context.
- Use the boundary case discriminators in §1.5, §2.5, §3.5, and §4.5 where \
the signal is ambiguous.
- **Cessation-without-repair.** If a deficit signal ceases in the focal turn \
without a corresponding repair action and without a positive engagement \
indicator from that component's §x.3 list, diagnose the cessation as \
accommodation or withdrawal, not resolution. Deficit-absent requires both \
cessation of the signal and evidence of repair.
- **Opening-turn constraint.** At turn 0, apply deficit labels only when the \
signal is unambiguous from the observable text alone, without requiring \
inference about the parties' shared background. Where the judgment depends on \
context the annotator cannot observe, label N. This constraint applies to all \
four components and lifts once sufficient observable context has accumulated.

Provide:
- A single-sentence rationale identifying the most salient signal in the \
focal turn
- A confidence score from 0.0 to 1.0 reflecting your certainty

Use the annotate_turn tool to return your response.\
"""

_ANNOTATE_TOOL = {
    "name": "annotate_turn",
    "description": "Return AARC deficit labels for the focal turn.",
    "input_schema": {
        "type": "object",
        "properties": {
            "acknowledgement_deficit": {
                "type": "boolean",
                "description": "True if an acknowledgement deficit is present.",
            },
            "agency_deficit": {
                "type": "boolean",
                "description": "True if an agency deficit is present.",
            },
            "reciprocity_deficit": {
                "type": "boolean",
                "description": "True if a reciprocity deficit is present.",
            },
            "clarity_deficit": {
                "type": "boolean",
                "description": "True if a clarity deficit is present.",
            },
            "rationale": {
                "type": "string",
                "description": "One sentence identifying the most salient deficit signal in the focal turn.",
            },
            "confidence": {
                "type": "number",
                "description": "Self-assessed annotation confidence, 0.0 (uncertain) to 1.0 (certain).",
            },
        },
        "required": [
            "acknowledgement_deficit",
            "agency_deficit",
            "reciprocity_deficit",
            "clarity_deficit",
            "rationale",
            "confidence",
        ],
    },
}


def _load_taxonomy(taxonomy_path: str) -> str:
    return Path(taxonomy_path).read_text(encoding="utf-8")


def _build_system_prompt(taxonomy_text: str) -> str:
    return _TASK_PREAMBLE + taxonomy_text + _TASK_INSTRUCTIONS


def make_turn_id(transcript_id: str, turn_index: int) -> str:
    return f"{transcript_id[:8]}-t{turn_index:04d}"


def format_context(transcript: Transcript, turn_index: int) -> str:
    """Format trailing 7-turn window ending at turn_index, focal turn marked ►."""
    turns = transcript["turns"]
    start = max(0, turn_index - 6)
    focal_turn = next(t for t in turns if t["turn_index"] == turn_index)
    focal_speaker = "Party A" if focal_turn["speaker"] == "party_a" else "Party B"
    lines = [f"Focal speaker: {focal_speaker}\n"]
    for turn in turns[start : turn_index + 1]:
        speaker = "Party A" if turn["speaker"] == "party_a" else "Party B"
        marker = "►" if turn["turn_index"] == turn_index else " "
        lines.append(f"  {marker} [{turn['turn_index']:2d}]  {speaker}: {turn['text']}")
    return "\n".join(lines)


def load_pre_annotations(path: str) -> list[PreAnnotation]:
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


def save_pre_annotation(annotation: PreAnnotation, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(annotation) + "\n")


async def preannotate_turn(
    transcript: Transcript,
    turn_index: int,
    client: AsyncAnthropic,
    taxonomy_text: str,
    *,
    model: str = "claude-opus-4-7",
) -> PreAnnotation:
    context = format_context(transcript, turn_index)
    system_prompt = _build_system_prompt(taxonomy_text)

    response = await client.messages.create(
        model=model,
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=[_ANNOTATE_TOOL],
        tool_choice={"type": "tool", "name": "annotate_turn"},
        messages=[{"role": "user", "content": f"Dialogue context:\n\n{context}"}],
    )

    tool_input = next(
        block.input
        for block in response.content
        if block.type == "tool_use" and block.name == "annotate_turn"
    )

    return PreAnnotation(
        turn_id=make_turn_id(transcript["id"], turn_index),
        transcript_id=transcript["id"],
        turn_index=turn_index,
        acknowledgement_deficit=tool_input["acknowledgement_deficit"],
        agency_deficit=tool_input["agency_deficit"],
        reciprocity_deficit=tool_input["reciprocity_deficit"],
        clarity_deficit=tool_input["clarity_deficit"],
        rationale=tool_input["rationale"],
        confidence=float(tool_input["confidence"]),
        model=model,
        annotation_date=date.today().isoformat(),
    )


async def preannotate_batch(
    transcripts: list[Transcript],
    taxonomy_path: str,
    output_path: str,
    batch_size: int,
    client: AsyncAnthropic,
    *,
    model: str = "claude-opus-4-7",
) -> int:
    """Annotate the next batch_size unannotated turns. Returns count processed."""
    taxonomy_text = _load_taxonomy(taxonomy_path)
    existing = {a["turn_id"] for a in load_pre_annotations(output_path)}

    pending = []
    for transcript in transcripts:
        for turn in transcript["turns"]:
            tid = make_turn_id(transcript["id"], turn["turn_index"])
            if tid not in existing:
                pending.append((transcript, turn["turn_index"]))

    batch = pending[:batch_size]
    if not batch:
        return 0

    count = 0
    for transcript, turn_index in batch:
        annotation = await preannotate_turn(
            transcript,
            turn_index,
            client,
            taxonomy_text,
            model=model,
        )
        save_pre_annotation(annotation, output_path)
        count += 1
        print(
            f"  [{count}/{len(batch)}]  {transcript['scenario_id']} t{turn_index:02d}  "
            f"A:{'Y' if annotation['acknowledgement_deficit'] else 'N'}  "
            f"Ag:{'Y' if annotation['agency_deficit'] else 'N'}  "
            f"R:{'Y' if annotation['reciprocity_deficit'] else 'N'}  "
            f"C:{'Y' if annotation['clarity_deficit'] else 'N'}  "
            f"({annotation['confidence']:.2f})  {annotation['rationale'][:60]}",
            flush=True,
        )

    return count


# ---------------------------------------------------------------------------
# Silver annotation — streamlined tool (no rationale, no confidence)
# ---------------------------------------------------------------------------

_SILVER_TASK_INSTRUCTIONS = """
## Annotation task

You will be given a dialogue excerpt. The focal turn is marked ► and its \
speaker is identified at the top of the context block. Your task is to answer \
a single question about that turn: *what does this utterance demonstrate about \
the focal speaker's evolving needs?* Labels are speaker-attributed — they \
describe what the speaker is currently experiencing or exhibiting, not what is \
being done to them.

For each of the four components, indicate whether a deficit is present (true) \
or absent (false). Note:
- Apply the diagnostic priority ordering: Acknowledgement → Agency → \
Reciprocity → Clarity. Where a turn could fall under two components, assign \
it to the earlier one.
- The unit of evidence is the trailing window, not the turn in isolation. Use \
the preceding turns as accumulating context.
- Use the boundary case discriminators in §1.5, §2.5, §3.5, and §4.5 where \
the signal is ambiguous.
- **Cessation-without-repair.** If a deficit signal ceases in the focal turn \
without a corresponding repair action and without a positive engagement \
indicator from that component's §x.3 list, diagnose the cessation as \
accommodation or withdrawal, not resolution. Deficit-absent requires both \
cessation of the signal and evidence of repair.
- **Opening-turn constraint.** At turn 0, apply deficit labels only when the \
signal is unambiguous from the observable text alone, without requiring \
inference about the parties' shared background. Where the judgment depends on \
context the annotator cannot observe, label N. This constraint applies to all \
four components and lifts once sufficient observable context has accumulated.

Use the annotate_turn tool to return your response.\
"""

_SILVER_ANNOTATE_TOOL = {
    "name": "annotate_turn",
    "description": "Return AARC deficit labels for the focal turn.",
    "input_schema": {
        "type": "object",
        "properties": {
            "acknowledgement_deficit": {
                "type": "boolean",
                "description": "True if an acknowledgement deficit is present.",
            },
            "agency_deficit": {
                "type": "boolean",
                "description": "True if an agency deficit is present.",
            },
            "reciprocity_deficit": {
                "type": "boolean",
                "description": "True if a reciprocity deficit is present.",
            },
            "clarity_deficit": {
                "type": "boolean",
                "description": "True if a clarity deficit is present.",
            },
        },
        "required": [
            "acknowledgement_deficit",
            "agency_deficit",
            "reciprocity_deficit",
            "clarity_deficit",
        ],
    },
}


def _build_silver_system_prompt(taxonomy_text: str) -> str:
    return _TASK_PREAMBLE + taxonomy_text + _SILVER_TASK_INSTRUCTIONS


def save_silver_annotation(annotation: TurnAnnotation, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(annotation) + "\n")


def load_silver_annotations(path: str) -> list[TurnAnnotation]:
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


async def silverannotate_turn(
    transcript: Transcript,
    turn_index: int,
    client: AsyncAnthropic,
    taxonomy_text: str,
    *,
    model: str = "claude-sonnet-4-6",
) -> TurnAnnotation:
    context = format_context(transcript, turn_index)
    system_prompt = _build_silver_system_prompt(taxonomy_text)

    response = await client.messages.create(
        model=model,
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        tools=[_SILVER_ANNOTATE_TOOL],
        tool_choice={"type": "tool", "name": "annotate_turn"},
        messages=[{"role": "user", "content": f"Dialogue context:\n\n{context}"}],
    )

    tool_input = next(
        block.input
        for block in response.content
        if block.type == "tool_use" and block.name == "annotate_turn"
    )

    return TurnAnnotation(
        turn_id=make_turn_id(transcript["id"], turn_index),
        transcript_id=transcript["id"],
        turn_index=turn_index,
        acknowledgement_deficit=tool_input["acknowledgement_deficit"],
        agency_deficit=tool_input["agency_deficit"],
        reciprocity_deficit=tool_input["reciprocity_deficit"],
        clarity_deficit=tool_input["clarity_deficit"],
        annotator_notes="",
        annotator_confidence=2,
        boundary_case=False,
        annotated_by=model,
        annotation_date=date.today().isoformat(),
    )


async def silverannotate_batch(
    transcripts: list[Transcript],
    taxonomy_path: str,
    output_path: str,
    batch_size: int,
    client: AsyncAnthropic,
    *,
    skip_ids: set[str] | None = None,
    model: str = "claude-sonnet-4-6",
) -> int:
    """Annotate the next batch_size unannotated turns. Returns count processed."""
    taxonomy_text = _load_taxonomy(taxonomy_path)
    existing_silver = {a["turn_id"] for a in load_silver_annotations(output_path)}
    skip = (skip_ids or set()) | existing_silver

    pending = []
    for transcript in transcripts:
        for turn in transcript["turns"]:
            tid = make_turn_id(transcript["id"], turn["turn_index"])
            if tid not in skip:
                pending.append((transcript, turn["turn_index"]))

    batch = pending[:batch_size]
    if not batch:
        return 0

    count = 0
    for transcript, turn_index in batch:
        annotation = await silverannotate_turn(
            transcript,
            turn_index,
            client,
            taxonomy_text,
            model=model,
        )
        save_silver_annotation(annotation, output_path)
        count += 1
        print(
            f"  [{count}/{len(batch)}]  {transcript['scenario_id']} t{turn_index:02d}  "
            f"A:{'Y' if annotation['acknowledgement_deficit'] else 'N'}  "
            f"Ag:{'Y' if annotation['agency_deficit'] else 'N'}  "
            f"R:{'Y' if annotation['reciprocity_deficit'] else 'N'}  "
            f"C:{'Y' if annotation['clarity_deficit'] else 'N'}",
            flush=True,
        )

    return count
