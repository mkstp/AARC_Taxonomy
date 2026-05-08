"""
Corpus plan script — enumerate scenario×persona×stylistics configs by TKI priority.

Outputs data/corpus_plan.jsonl: the stable manifest that generate_corpus.py loads
instead of its hardcoded PLAN. Re-run with --write after changing --per-scenario
to extend the plan; newly done configs will be reflected automatically.

TKI priority tiers (lower = higher priority):
  1  competing × competing
  2  competing × avoiding
  3  avoiding × avoiding
  4  competing × collaborating
  (5 accommodating × accommodating — impossible: only one Ac persona in library)
  6  competing × accommodating
  7  avoiding × accommodating
  8  collaborating × avoiding
  9  collaborating × accommodating
 10  compromising × anything
 11  other (e.g. collaborating × collaborating)

Usage:
    python3 scripts/plan_corpus.py                   # show status, no write
    python3 scripts/plan_corpus.py --write           # write data/corpus_plan.jsonl
    python3 scripts/plan_corpus.py --pending         # show only pending configs
    python3 scripts/plan_corpus.py --per-scenario 5  # configs per scenario (default: 5)
"""

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from fpo_mediation.corpus_manager import load_all
from fpo_mediation.persona_scenario_library import (
    load_personas,
    load_scenarios,
    load_stylistics_profiles,
)

CORPUS = ROOT / "data" / "corpus.jsonl"
PERSONAS = ROOT / "data" / "personas.json"
SCENARIOS = ROOT / "data" / "scenarios.json"
STYLISTICS = ROOT / "data" / "stylistics_profiles.json"
PLAN_OUT = ROOT / "data" / "corpus_plan.jsonl"

# Seed for stable tiebreaking within tiers and stylistics assignment.
SEED = 42

# Unordered (sorted) TKI mode pair → priority tier.
_TKI_TIERS: dict[tuple[str, str], int] = {
    ("competing", "competing"): 1,
    ("avoiding", "competing"): 2,
    ("avoiding", "avoiding"): 3,
    ("collaborating", "competing"): 4,
    ("accommodating", "accommodating"): 5,
    ("accommodating", "competing"): 6,
    ("accommodating", "avoiding"): 7,
    ("avoiding", "collaborating"): 8,
    ("accommodating", "collaborating"): 9,
}

_TIER_LABELS: dict[int, str] = {
    1: "C×C",
    2: "C×Av",
    3: "Av×Av",
    4: "C×Co",
    5: "Ac×Ac",
    6: "C×Ac",
    7: "Av×Ac",
    8: "Co×Av",
    9: "Co×Ac",
    10: "Cm×?",
    11: "other",
}


def tki_tier(mode_a: str, mode_b: str) -> int:
    key = tuple(sorted([mode_a, mode_b]))
    if "compromising" in key:
        return 10
    return _TKI_TIERS.get(key, 11)


def _stylistics_pair(
    stylistics: list[dict], sc_id: str, pa_id: str, pb_id: str
) -> tuple[str, str]:
    """Assign stylistics profiles via seeded sampling — matches generate_corpus.py logic."""
    seed = hash((sc_id, pa_id, pb_id)) % (2**32)
    rng = random.Random(seed)
    return rng.choice(stylistics)["id"], rng.choice(stylistics)["id"]


def _existing_configs(corpus_path: Path) -> set[tuple[str, str, str]]:
    return {
        (t["scenario_id"], t["persona_a_id"], t["persona_b_id"])
        for t in load_all(str(corpus_path))
    }


def build_plan(
    personas: list[dict],
    scenarios: list[dict],
    stylistics: list[dict],
    existing: set[tuple[str, str, str]],
    per_scenario: int,
) -> list[dict]:
    """Build the corpus plan ordered by scenario, then TKI tier within scenario.

    For each scenario:
    - All existing done configs are included first (regardless of TKI tier).
    - Remaining slots (up to per_scenario) are filled with highest-priority pending pairs.
    - If done configs already exceed per_scenario, all are kept and the plan grows.
    """
    tki_map = {p["id"]: p["tki_primary_mode"] for p in personas}
    plan: list[dict] = []

    for scenario in sorted(scenarios, key=lambda s: s["id"]):
        sc_id = scenario["id"]
        rng = random.Random(hash(sc_id) ^ SEED)

        # All unordered persona pairs with tier + random tiebreak for stable ordering.
        candidates: list[tuple[int, float, str, str]] = []
        for i, pa in enumerate(personas):
            for pb in personas[i + 1 :]:
                tier = tki_tier(tki_map[pa["id"]], tki_map[pb["id"]])
                candidates.append((tier, rng.random(), pa["id"], pb["id"]))
        candidates.sort(key=lambda x: (x[0], x[1]))

        done: list[tuple[int, str, str]] = []
        pending: list[tuple[int, str, str]] = []
        for tier, _, pa_id, pb_id in candidates:
            if (sc_id, pa_id, pb_id) in existing or (sc_id, pb_id, pa_id) in existing:
                done.append((tier, pa_id, pb_id))
            else:
                pending.append((tier, pa_id, pb_id))

        remaining_slots = max(0, per_scenario - len(done))

        # Group pending by tier; candidates are already sorted (tier, tiebreak).
        pending_by_tier: dict[int, list[tuple[int, str, str]]] = {}
        for item in pending:
            pending_by_tier.setdefault(item[0], []).append(item)

        done_tiers = {t for t, _, _ in done}

        # Pass 1: one from each tier not already covered by a done config, in priority order.
        selected_pending: list[tuple[int, str, str]] = []
        for tier in sorted(pending_by_tier.keys()):
            if len(selected_pending) >= remaining_slots:
                break
            if tier not in done_tiers:
                selected_pending.append(pending_by_tier[tier][0])
                done_tiers.add(tier)  # mark covered so we don't double-pick this tier

        # Pass 2: fill any remaining slots with the highest-priority candidates (tier 1 first).
        for item in pending:
            if len(selected_pending) >= remaining_slots:
                break
            if item not in selected_pending:
                selected_pending.append(item)

        for tier, pa_id, pb_id in done:
            sty_a, sty_b = _stylistics_pair(stylistics, sc_id, pa_id, pb_id)
            plan.append({
                "scenario_id": sc_id,
                "persona_a_id": pa_id,
                "persona_b_id": pb_id,
                "stylistics_a_id": sty_a,
                "stylistics_b_id": sty_b,
                "tki_a": tki_map[pa_id],
                "tki_b": tki_map[pb_id],
                "tki_tier": tier,
                "status": "done",
            })

        for tier, pa_id, pb_id in selected_pending:
            sty_a, sty_b = _stylistics_pair(stylistics, sc_id, pa_id, pb_id)
            plan.append({
                "scenario_id": sc_id,
                "persona_a_id": pa_id,
                "persona_b_id": pb_id,
                "stylistics_a_id": sty_a,
                "stylistics_b_id": sty_b,
                "tki_a": tki_map[pa_id],
                "tki_b": tki_map[pb_id],
                "tki_tier": tier,
                "status": "pending",
            })

    return plan


def report(
    plan: list[dict],
    scenarios: list[dict],
    personas: list[dict],
    stylistics: list[dict],
    pending_only: bool,
) -> None:
    scenario_map = {s["id"]: s.get("title", s["id"]) for s in scenarios}
    persona_map = {p["id"]: p["name"] for p in personas}
    stylistics_map = {s["id"]: s["label"] for s in stylistics}

    done_count = sum(1 for e in plan if e["status"] == "done")
    pending_count = sum(1 for e in plan if e["status"] == "pending")

    print(f"\nCorpus plan: {len(plan)} configs ({done_count} done, {pending_count} pending)\n")

    col = f"  {'Status':<8}  {'Scenario':<40}  {'Party A':<12}  {'Party B':<12}  {'Tier':<8}  Stylistics A / B"
    print(col)
    print("  " + "-" * (len(col) + 4))

    for entry in plan:
        if pending_only and entry["status"] == "done":
            continue
        sc_title = scenario_map.get(entry["scenario_id"], entry["scenario_id"])[:38]
        pa_name = persona_map.get(entry["persona_a_id"], entry["persona_a_id"])
        pb_name = persona_map.get(entry["persona_b_id"], entry["persona_b_id"])
        tier_lbl = _TIER_LABELS.get(entry["tki_tier"], f"tier{entry['tki_tier']}")
        sty_a = stylistics_map.get(entry["stylistics_a_id"], entry["stylistics_a_id"])
        sty_b = stylistics_map.get(entry["stylistics_b_id"], entry["stylistics_b_id"])
        print(
            f"  {entry['status']:<8}  {sc_title:<40}  {pa_name:<12}  {pb_name:<12}"
            f"  {tier_lbl:<8}  {sty_a} / {sty_b}"
        )

    tier_counts = Counter((e["tki_tier"], e["status"]) for e in plan)
    print(f"\nTier distribution:")
    for tier in sorted({e["tki_tier"] for e in plan}):
        d = tier_counts.get((tier, "done"), 0)
        p = tier_counts.get((tier, "pending"), 0)
        lbl = _TIER_LABELS.get(tier, f"tier{tier}")
        print(f"  Tier {tier:2d}  {lbl:<8}  done={d}  pending={p}")


def write_plan(plan: list[dict], path: Path) -> None:
    with open(path, "w") as f:
        for entry in plan:
            f.write(json.dumps(entry) + "\n")
    print(f"\nWrote {len(plan)} entries to {path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Corpus plan — TKI-priority config manifest.")
    parser.add_argument("--write", action="store_true", help="Write data/corpus_plan.jsonl")
    parser.add_argument("--pending", action="store_true", help="Show only pending configs")
    parser.add_argument(
        "--per-scenario",
        type=int,
        default=5,
        metavar="N",
        help="Target configs per scenario (default: 5, giving 100 total across 20 scenarios)",
    )
    args = parser.parse_args()

    personas = load_personas(str(PERSONAS))
    scenarios = load_scenarios(str(SCENARIOS))
    stylistics = load_stylistics_profiles(str(STYLISTICS))
    existing = _existing_configs(CORPUS)

    plan = build_plan(personas, scenarios, stylistics, existing, per_scenario=args.per_scenario)
    report(plan, scenarios, personas, stylistics, pending_only=args.pending)

    if args.write:
        write_plan(plan, PLAN_OUT)
    else:
        print("\n(Pass --write to persist the plan to data/corpus_plan.jsonl)")


if __name__ == "__main__":
    main()
