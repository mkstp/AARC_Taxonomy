"""
Batch corpus generation — generates all pending configs from data/corpus_plan.jsonl.

Checks the corpus for already-completed configurations and skips them,
so this script is safe to re-run after a partial failure.

Run scripts/plan_corpus.py --write first to generate or refresh the plan.

Usage:
    python3 scripts/generate_corpus.py              # run all missing configs
    python3 scripts/generate_corpus.py --dry-run    # show plan without generating
    python3 scripts/generate_corpus.py --concurrency 3
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from anthropic import AsyncAnthropic

from fpo_mediation.corpus_manager import get_stats, load_all, save_transcript
from fpo_mediation.dialogue_generator import generate_dialogue
from fpo_mediation.persona_scenario_library import (
    load_personas,
    load_scenarios,
    load_stylistics_profiles,
)

CORPUS = str(ROOT / "data" / "corpus.jsonl")
PERSONAS = str(ROOT / "data" / "personas.json")
SCENARIOS = str(ROOT / "data" / "scenarios.json")
STYLISTICS = str(ROOT / "data" / "stylistics_profiles.json")
PLAN_FILE = str(ROOT / "data" / "corpus_plan.jsonl")


def _load_plan(plan_path: str) -> list[dict]:
    """Load all entries from corpus_plan.jsonl."""
    entries = []
    with open(plan_path) as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries


def _existing_configs(corpus_path: str) -> set[tuple[str, str, str]]:
    return {
        (t["scenario_id"], t["persona_a_id"], t["persona_b_id"])
        for t in load_all(corpus_path)
    }


async def _generate_and_save(
    persona_a: dict,
    persona_b: dict,
    scenario: dict,
    stylistics_a: dict,
    stylistics_b: dict,
    label: str,
    sem: asyncio.Semaphore,
    client: AsyncAnthropic,
) -> bool:
    async with sem:
        print(f"  → {label}", flush=True)
        try:
            transcript = await generate_dialogue(
                persona_a, persona_b, scenario,
                client=client,
                stylistics_a=stylistics_a,
                stylistics_b=stylistics_b,
            )
            save_transcript(transcript, CORPUS)
            print(
                f"  ✓ {label}  "
                f"({transcript['termination_reason']}, {len(transcript['turns'])} turns, "
                f"sty: {stylistics_a['label']} / {stylistics_b['label']})",
                flush=True,
            )
            return True
        except Exception as exc:
            print(f"  ✗ {label}: {exc}", flush=True)
            return False


async def main() -> None:
    parser = argparse.ArgumentParser(description="Batch corpus generation.")
    parser.add_argument("--dry-run", action="store_true", help="Show plan without generating")
    parser.add_argument("--concurrency", type=int, default=3, help="Max concurrent dialogues")
    parser.add_argument("--limit", type=int, default=None, metavar="N", help="Generate at most N dialogues")
    args = parser.parse_args()

    personas = load_personas(PERSONAS)
    scenarios = load_scenarios(SCENARIOS)
    stylistics = load_stylistics_profiles(STYLISTICS)
    persona_map = {p["id"]: p for p in personas}
    scenario_map = {s["id"]: s for s in scenarios}
    stylistics_map = {s["id"]: s for s in stylistics}

    plan = _load_plan(PLAN_FILE)
    existing = _existing_configs(CORPUS)

    # A plan entry is pending if neither its canonical nor reversed ordering is in the corpus.
    def _is_pending(entry: dict) -> bool:
        sc, pa, pb = entry["scenario_id"], entry["persona_a_id"], entry["persona_b_id"]
        return (sc, pa, pb) not in existing and (sc, pb, pa) not in existing

    pending_entries = [e for e in plan if _is_pending(e)]
    done_count = len(plan) - len(pending_entries)

    print(f"\nCorpus plan: {len(plan)} configs ({done_count} done, {len(pending_entries)} to generate)")

    if not pending_entries:
        print("Corpus is complete.")
        return

    print(f"\n{'Status':<8}  {'Scenario':<40}  {'Party A':<10}  {'Party B':<10}  {'Tier':<6}  {'Stylistics A / B'}")
    print("-" * 110)
    for entry in plan:
        sc = scenario_map[entry["scenario_id"]]
        pa = persona_map[entry["persona_a_id"]]
        pb = persona_map[entry["persona_b_id"]]
        sty_a = stylistics_map[entry["stylistics_a_id"]]
        sty_b = stylistics_map[entry["stylistics_b_id"]]
        status = "pending" if _is_pending(entry) else "done"
        tier = entry.get("tki_tier", "?")
        print(
            f"  {status:<6}  {sc.get('title', entry['scenario_id']):<40}  "
            f"{pa['name']:<10}  {pb['name']:<10}  {tier:<6}  {sty_a['label']} / {sty_b['label']}"
        )

    if args.dry_run:
        return

    if args.limit is not None:
        pending_entries = pending_entries[: args.limit]

    print(f"\nGenerating {len(pending_entries)} dialogue(s) with concurrency={args.concurrency}...\n")

    client = AsyncAnthropic()
    sem = asyncio.Semaphore(args.concurrency)

    tasks = []
    for entry in pending_entries:
        sc = scenario_map[entry["scenario_id"]]
        pa = persona_map[entry["persona_a_id"]]
        pb = persona_map[entry["persona_b_id"]]
        sty_a = stylistics_map[entry["stylistics_a_id"]]
        sty_b = stylistics_map[entry["stylistics_b_id"]]
        label = f"{sc.get('title', entry['scenario_id']):<40}  {pa['name']} vs {pb['name']}"
        tasks.append(_generate_and_save(pa, pb, sc, sty_a, sty_b, label, sem, client))

    results = await asyncio.gather(*tasks)
    succeeded = sum(results)
    failed = len(results) - succeeded

    stats = get_stats(CORPUS)
    print(f"\nDone. {succeeded} generated, {failed} failed.")
    print(f"Corpus: {stats['total']} total, {stats['avg_turns']:.1f} avg turns")


if __name__ == "__main__":
    asyncio.run(main())
