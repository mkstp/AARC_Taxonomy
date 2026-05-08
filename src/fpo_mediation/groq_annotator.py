"""Groq-powered silver annotation — Qwen counterpart to gpt_annotator."""

import asyncio
import json
import os
from datetime import date
from pathlib import Path

from groq import AsyncGroq

from .models import TurnAnnotation, Transcript
from .claude_annotator import (
    _TASK_PREAMBLE,
    _SILVER_TASK_INSTRUCTIONS,
    make_turn_id,
    format_context,
    save_silver_annotation,
    load_silver_annotations,
)

_GROQ_ANNOTATE_TOOL = {
    "type": "function",
    "function": {
        "name": "annotate_turn",
        "description": "Return AARC deficit labels for the focal turn.",
        "parameters": {
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
    },
}


def make_groq_client() -> AsyncGroq:
    api_key = os.environ.get("GROC_QWEN_API_KEY")
    if not api_key:
        raise EnvironmentError("GROC_QWEN_API_KEY not set")
    return AsyncGroq(api_key=api_key)


def _load_taxonomy(taxonomy_path: str) -> str:
    return Path(taxonomy_path).read_text(encoding="utf-8")


def _build_system_prompt(taxonomy_text: str) -> str:
    return _TASK_PREAMBLE + taxonomy_text + _SILVER_TASK_INSTRUCTIONS


async def silverannotate_turn(
    transcript: Transcript,
    turn_index: int,
    client: AsyncGroq,
    taxonomy_text: str,
    *,
    model: str,
) -> TurnAnnotation:
    context = format_context(transcript, turn_index)
    system_prompt = _build_system_prompt(taxonomy_text)

    # Retry loop for rate limit errors (429)
    delay = 60
    last_exc: Exception | None = None
    response = None
    for attempt in range(5):
        try:
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Dialogue context:\n\n{context}"},
                ],
                tools=[_GROQ_ANNOTATE_TOOL],
                tool_choice={"type": "function", "function": {"name": "annotate_turn"}},
            )
            break
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"  Rate limit hit (attempt {attempt+1}/5), waiting {delay}s ...", flush=True)
                last_exc = e
                await asyncio.sleep(delay)
                delay = min(delay * 2, 300)
            else:
                raise
    if response is None:
        raise RuntimeError(f"All retry attempts exhausted due to rate limits") from last_exc

    tool_call = response.choices[0].message.tool_calls[0]
    tool_input = json.loads(tool_call.function.arguments)

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
    client: AsyncGroq,
    *,
    skip_ids: set[str] | None = None,
    model: str,
) -> int:
    """Annotate the next batch_size turns. Returns count processed."""
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
        # Pacing: Groq qwen3-32b has a 6,000 TPM ceiling; brief sleep prevents 429s.
        await asyncio.sleep(2)

    return count
