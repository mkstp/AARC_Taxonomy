"""
Render transcripts from corpus.jsonl in a human-readable format.

Usage:
    python3 scripts/render.py                      # list all transcripts
    python3 scripts/render.py --index 0            # render first transcript
    python3 scripts/render.py --id <uuid-prefix>   # render by ID
    python3 scripts/render.py --all                # render every transcript
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

from fpo_mediation.corpus_manager import load_all, get_stats
from fpo_mediation.persona_scenario_library import load_personas, load_scenarios

CORPUS = str(ROOT / "data" / "corpus.jsonl")
PERSONAS = str(ROOT / "data" / "personas.json")
SCENARIOS = str(ROOT / "data" / "scenarios.json")

WIDTH = 70


def render_transcript(transcript: dict, persona_map: dict, scenario_map: dict) -> None:
    pa = persona_map.get(transcript["persona_a_id"], {})
    pb = persona_map.get(transcript["persona_b_id"], {})
    sc = scenario_map.get(transcript["scenario_id"], {})

    gold_marker = " [GOLD]" if transcript.get("is_gold") else ""
    print("\n" + "=" * WIDTH)
    print(f"TRANSCRIPT  {transcript['id'][:8]}{gold_marker}")
    print("=" * WIDTH)
    print(f"Scenario:   {sc.get('title', transcript['scenario_id'])}")
    print(f"Party A:    {pa.get('name', transcript['persona_a_id'])}")
    print(f"Party B:    {pb.get('name', transcript['persona_b_id'])}")
    print(f"End state:  {transcript['termination_reason']}")
    print(f"Turns:      {len(transcript['turns'])}")
    print("-" * WIDTH)

    for turn in transcript["turns"]:
        speaker_id = turn["speaker"]
        name = pa.get("name", "Party A") if speaker_id == "party_a" else pb.get("name", "Party B")
        if turn.get("director_note"):
            print(f"\n  [DIRECTOR] {turn['director_note']}")
        print(f"\n[{turn['turn_index']:02d}] {name}")
        if turn.get("reasoning"):
            snippet = turn["reasoning"][:120]
            ellipsis = "..." if len(turn["reasoning"]) > 120 else ""
            print(f"  <thinking> {snippet}{ellipsis} </thinking>")
        print(f"  {turn['text']}")

    print("\n" + "=" * WIDTH)


def render_listing(transcripts: list) -> None:
    if not transcripts:
        print("Corpus is empty.")
        return
    print(f"\n{'#':<4}  {'ID':<10}  {'Scenario':<36}  {'Turns':<6}  {'End state':<12}  Gold")
    print("-" * 78)
    for i, t in enumerate(transcripts):
        gold = "yes" if t.get("is_gold") else ""
        scenario_id = t.get("scenario_id", "")
        print(f"{i:<4}  {t['id'][:8]:<10}  {scenario_id:<36}  {len(t['turns']):<6}  {t['termination_reason']:<12}  {gold}")
    stats = get_stats(CORPUS)
    print(f"\n{stats['total']} transcripts  |  {stats['gold_count']} gold  |  {stats['avg_turns']:.1f} avg turns")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render corpus transcripts.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--index", type=int, help="Render transcript at this index (0-based)")
    group.add_argument("--id", type=str, help="Render transcript matching this ID prefix")
    group.add_argument("--all", action="store_true", help="Render every transcript")
    parser.add_argument("--no-thinking", action="store_true", help="Omit reasoning blocks")
    parser.add_argument("--no-director", action="store_true", help="Omit director notes")
    args = parser.parse_args()

    transcripts = load_all(CORPUS)
    if not transcripts:
        print("Corpus is empty.")
        return

    personas = load_personas(PERSONAS)
    scenarios = load_scenarios(SCENARIOS)
    persona_map = {p["id"]: p for p in personas}
    scenario_map = {s["id"]: s for s in scenarios}

    if args.index is not None:
        if args.index >= len(transcripts):
            print(f"Index {args.index} out of range (corpus has {len(transcripts)} transcripts).")
            sys.exit(1)
        target = [transcripts[args.index]]
    elif args.id:
        target = [t for t in transcripts if t["id"].startswith(args.id)]
        if not target:
            print(f"No transcript found with ID prefix {args.id!r}.")
            sys.exit(1)
    elif args.all:
        target = transcripts
    else:
        render_listing(transcripts)
        return

    if args.no_thinking:
        for t in target:
            for turn in t["turns"]:
                turn["reasoning"] = ""
    if args.no_director:
        for t in target:
            for turn in t["turns"]:
                turn["director_note"] = ""

    for t in target:
        render_transcript(t, persona_map, scenario_map)


if __name__ == "__main__":
    main()
