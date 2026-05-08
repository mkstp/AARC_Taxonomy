"""MOD-003: CorpusManager — Implements DEL-005, DEL-006. Validated by VC-04."""

import json
from pathlib import Path

from .models import Transcript


def save_transcript(transcript: Transcript, path: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(transcript) + "\n")


def load_transcript(transcript_id: str, path: str) -> Transcript:
    for record in _iter_records(path):
        if record["id"] == transcript_id:
            return record
    raise KeyError(f"Transcript {transcript_id!r} not found in {path}")


def load_all(path: str, gold_only: bool = False) -> list[Transcript]:
    records = list(_iter_records(path))
    if gold_only:
        return [r for r in records if r["is_gold"]]
    return records


def mark_gold(transcript_id: str, path: str) -> None:
    records = list(_iter_records(path))
    found = False
    for record in records:
        if record["id"] == transcript_id:
            record["is_gold"] = True
            found = True
            break
    if not found:
        raise KeyError(f"Transcript {transcript_id!r} not found in {path}")
    _rewrite(records, path)


def get_stats(path: str) -> dict:
    records = list(_iter_records(path))
    gold_count = sum(1 for r in records if r["is_gold"])
    avg_turns = (
        sum(len(r["turns"]) for r in records) / len(records) if records else 0.0
    )
    return {"total": len(records), "gold_count": gold_count, "avg_turns": avg_turns}


def _iter_records(path: str):
    p = Path(path)
    if not p.exists():
        return
    with p.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def _rewrite(records: list[Transcript], path: str) -> None:
    p = Path(path)
    with p.open("w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
