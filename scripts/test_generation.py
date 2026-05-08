"""
Live generation test — runs one dialogue end-to-end and prints the transcript.

Usage:
    ANTHROPIC_API_KEY=sk-... python3 scripts/test_generation.py
    python3 scripts/test_generation.py --scenario 1 --persona-a 0 --persona-b 4
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from fpo_mediation.corpus_manager import get_stats, save_transcript
from fpo_mediation.dialogue_generator import generate_dialogue
from fpo_mediation.persona_scenario_library import load_personas, load_scenarios


def print_transcript(transcript: dict, personas: list, scenarios: list) -> None:
    persona_map = {p["id"]: p for p in personas}
    scenario_map = {s["id"]: s for s in scenarios}

    pa = persona_map[transcript["persona_a_id"]]
    pb = persona_map[transcript["persona_b_id"]]
    sc = scenario_map[transcript["scenario_id"]]

    print("\n" + "=" * 70)
    print(f"TRANSCRIPT  {transcript['id'][:8]}")
    print("=" * 70)
    print(f"Scenario:   {sc['title']}")
    print(f"Party A:    {pa['name']} — {pa['core_needs'][:60]}...")
    print(f"Party B:    {pb['name']} — {pb['core_needs'][:60]}...")
    print(f"End state:  {transcript['termination_reason']}")
    print(f"Turns:      {len(transcript['turns'])}")
    print("-" * 70)

    for turn in transcript["turns"]:
        name = pa["name"] if turn["speaker"] == "party_a" else pb["name"]
        if turn.get("director_note"):
            print(f"\n  [DIRECTOR] {turn['director_note']}")
        print(f"\n[{turn['turn_index']:02d}] {name}")
        if turn["reasoning"]:
            print(f"  <thinking> {turn['reasoning'][:120]}{'...' if len(turn['reasoning']) > 120 else ''} </thinking>")
        print(f"  {turn['text']}")

    print("\n" + "=" * 70)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", type=int, default=1, help="Scenario number (1–20)")
    parser.add_argument("--persona-a", type=int, default=0, help="Persona A index (0–14)")
    parser.add_argument("--persona-b", type=int, default=4, help="Persona B index (0–14)")
    parser.add_argument("--min-turns", type=int, default=8)
    parser.add_argument("--max-turns", type=int, default=16)
    args = parser.parse_args()

    personas = load_personas(str(ROOT / "data" / "personas.json"))
    scenarios = load_scenarios(str(ROOT / "data" / "scenarios.json"))

    persona_a = personas[args.persona_a]
    persona_b = personas[args.persona_b]
    scenario = scenarios[args.scenario - 1]

    print(f"\nGenerating dialogue...")
    print(f"  Scenario {args.scenario}: {scenario['title']}")
    print(f"  Party A: {persona_a['name']} (persona-{args.persona_a + 1:03d})")
    print(f"  Party B: {persona_b['name']} (persona-{args.persona_b + 1:03d})")
    print(f"  Turn range: {args.min_turns}–{args.max_turns}")

    transcript = await generate_dialogue(
        persona_a, persona_b, scenario,
        min_turns=args.min_turns,
        max_turns=args.max_turns,
    )

    print_transcript(transcript, personas, scenarios)

    corpus_path = str(ROOT / "data" / "corpus.jsonl")
    save_transcript(transcript, corpus_path)
    stats = get_stats(corpus_path)
    print(f"\nSaved to {corpus_path}")
    print(f"Corpus stats: {stats['total']} total, {stats['gold_count']} gold, {stats['avg_turns']:.1f} avg turns")


if __name__ == "__main__":
    asyncio.run(main())
