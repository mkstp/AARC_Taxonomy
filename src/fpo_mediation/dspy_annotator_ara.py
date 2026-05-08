"""DSPy-optimized 3-label silver annotation (Acknowledgement, Agency, Reciprocity).

Clarity is excluded from the output signature and optimization metric — its failure
is a taxonomy grounding problem deferred to a future annotation pass (see FPO-aq6).
Use this annotator when scaling A/G/R annotation to the full corpus.
"""

from datetime import date
from pathlib import Path

import dspy

from .models import TurnAnnotation, Transcript
from .claude_annotator import (
    make_turn_id,
    format_context,
    save_silver_annotation,
    load_silver_annotations,
)

LABELS = ["acknowledgement_deficit", "agency_deficit", "reciprocity_deficit"]

ROOT = Path(__file__).parent.parent.parent

DEFAULT_PROGRAM_PATH = str(ROOT / "data" / "dspy_program_ara.json")


class AGRAnnotation(dspy.Signature):
    """Annotate a single dialogue turn for AARC deficit signals.

    Apply the diagnostic priority ordering: Acknowledgement → Agency → Reciprocity.
    Labels are speaker-attributed: they describe what the focal speaker is currently
    exhibiting or lacking, not what is being done to them. Use the trailing context window
    to assess accumulating patterns. A deficit is absent only when there is positive evidence
    of resolution or repair — cessation alone is not sufficient."""

    dialogue_context: str = dspy.InputField(
        desc="Formatted dialogue excerpt. Focal speaker identified at top; focal turn marked ►; 7-turn context window."
    )
    acknowledgement_deficit: bool = dspy.OutputField(
        desc="True if the focal speaker exhibits an unmet need for recognition — hedging their own legitimacy, cataloguing grievances, or recruiting imagined consensus to validate unacknowledged experience."
    )
    agency_deficit: bool = dspy.OutputField(
        desc="True if the focal speaker exhibits perceived foreclosure on their ability to influence the situation — explicit constraint narratives, procedural avoidance, or nominal disengaged participation."
    )
    reciprocity_deficit: bool = dspy.OutputField(
        desc="True if the focal speaker treats the interaction as positional or zero-sum: positional language, withholding, stockpiling grievances as leverage, or dismissing the other party's standing."
    )


class AGRAnnotator(dspy.Module):
    def __init__(self) -> None:
        self.predict = dspy.Predict(AGRAnnotation)

    def forward(self, dialogue_context: str) -> dspy.Prediction:
        return self.predict(dialogue_context=dialogue_context)


def load_program(program_path: str = DEFAULT_PROGRAM_PATH) -> AGRAnnotator:
    program = AGRAnnotator()
    program.load(program_path)
    return program


async def silverannotate_batch(
    transcripts: list[Transcript],
    taxonomy_path: str,  # unused: taxonomy is compiled into the program
    output_path: str,
    batch_size: int,
    client,  # unused: DSPy manages its own LM
    *,
    skip_ids: set[str] | None = None,
    model: str = "openai/gpt-5.4",
    program_path: str = DEFAULT_PROGRAM_PATH,
) -> int:
    """Annotate using the compiled AGR MiPROv2 program. Returns count processed.

    clarity_deficit is always written as False; annotated_by encodes the annotator type
    so downstream consumers can identify ARA-sourced annotations.
    """
    lm = dspy.LM(model, max_tokens=128, temperature=0.0)
    dspy.configure(lm=lm)
    program = load_program(program_path)

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
        context = format_context(transcript, turn_index)
        pred = program(dialogue_context=context)

        annotation = TurnAnnotation(
            turn_id=make_turn_id(transcript["id"], turn_index),
            transcript_id=transcript["id"],
            turn_index=turn_index,
            acknowledgement_deficit=bool(pred.acknowledgement_deficit),
            agency_deficit=bool(pred.agency_deficit),
            reciprocity_deficit=bool(pred.reciprocity_deficit),
            clarity_deficit=False,  # not assessed by AGR annotator
            annotator_notes="clarity_deficit not assessed (AGR annotator; see FPO-aq6)",
            annotator_confidence=2,
            boundary_case=False,
            annotated_by=f"dspy-ara/{model}",
            annotation_date=date.today().isoformat(),
        )
        save_silver_annotation(annotation, output_path)
        count += 1
        print(
            f"  [{count}/{len(batch)}]  {transcript['scenario_id']} t{turn_index:02d}  "
            f"A:{'Y' if annotation['acknowledgement_deficit'] else 'N'}  "
            f"G:{'Y' if annotation['agency_deficit'] else 'N'}  "
            f"R:{'Y' if annotation['reciprocity_deficit'] else 'N'}",
            flush=True,
        )

    return count
