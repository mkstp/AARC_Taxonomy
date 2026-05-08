"""DSPy-optimized silver annotation — loads a compiled MiPROv2 program for inference."""

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

LABELS = ["acknowledgement_deficit", "agency_deficit", "reciprocity_deficit", "clarity_deficit"]

ROOT = Path(__file__).parent.parent.parent

DEFAULT_PROGRAM_PATH = str(ROOT / "data" / "dspy_program.json")


class AARCAnnotation(dspy.Signature):
    """Annotate a single dialogue turn for AARC deficit signals.

    Apply the diagnostic priority ordering: Acknowledgement → Agency → Reciprocity → Clarity.
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
    clarity_deficit: bool = dspy.OutputField(
        desc="True if the focal speaker silently crosses an epistemic gap — proceeds on unverified intent attribution, overcertain inference, or vague language that persists despite concrete engagement from the other party. Naming a gap and inviting resolution is a repair move, not a deficit."
    )


class AARCAnnotator(dspy.Module):
    def __init__(self) -> None:
        self.predict = dspy.Predict(AARCAnnotation)

    def forward(self, dialogue_context: str) -> dspy.Prediction:
        return self.predict(dialogue_context=dialogue_context)


def load_program(program_path: str = DEFAULT_PROGRAM_PATH) -> AARCAnnotator:
    program = AARCAnnotator()
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
    """Annotate using the compiled MiPROv2 program. Returns count processed."""
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
            clarity_deficit=bool(pred.clarity_deficit),
            annotator_notes="",
            annotator_confidence=2,
            boundary_case=False,
            annotated_by=f"dspy/{model}",
            annotation_date=date.today().isoformat(),
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
