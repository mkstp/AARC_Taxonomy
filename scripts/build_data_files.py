"""
Parse dialogue generation assets and produce data/personas.json and data/scenarios.json.

Persona names are assigned sequentially; they have no canonical name in the character library.
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).parent.parent
ASSETS = ROOT / "docs" / "dialogue_gen_assets"
DATA = ROOT / "data"

# Neutral names assigned to characters 1–15 in order
PERSONA_NAMES = [
    "Morgan", "Casey", "Riley", "Alex", "Jordan",
    "Sam", "Taylor", "Jamie", "Drew", "Quinn",
    "Blair", "Reese", "Avery", "Logan", "Kendall",
]


def parse_personas(path: Path) -> list[dict]:
    text = path.read_text()
    # Split on character section headers: ## Character N — ...
    sections = re.split(r"^## Character \d+", text, flags=re.MULTILINE)
    sections = [s.strip() for s in sections if s.strip() and not s.strip().startswith("#")]

    personas = []
    for i, section in enumerate(sections):
        fields = _extract_persona_fields(section)
        fields["id"] = f"persona-{i + 1:03d}"
        fields["name"] = PERSONA_NAMES[i]
        personas.append(fields)
    return personas


def _extract_persona_fields(section: str) -> dict:
    # Field names in the markdown (with optional trailing period or colon variant)
    mapping = {
        "CORE_NEEDS": "core_needs",
        "BELIEFS_ABOUT_SELF": "beliefs_about_self",
        "BELIEFS_ABOUT_OTHERS": "beliefs_about_others",
        "TKI_PRIMARY_MODE": "tki_primary_mode",
        "STORM_SHIFT": "storm_shift",
        "ACTIVATION_PROFILE": "activation_profile",
        "REPAIR_ORIENTATION": "repair_orientation",
        "FACE_SALIENCE": "face_salience",
        "COMMUNICATIVE_REGISTER": "communicative_register",
    }
    result = {}
    for md_key, json_key in mapping.items():
        # Match **FIELD_NAME** or **FIELD_NAME**. or **FIELD_NAME:** followed by value
        pattern = rf"\*\*{md_key}\*\*[.:]?\s+(.+?)(?=\n\*\*|\n---|\Z)"
        m = re.search(pattern, section, re.DOTALL)
        if m:
            result[json_key] = m.group(1).strip()
        else:
            result[json_key] = ""
    return result


def _extract_field(text: str, field_name: str) -> str:
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s+(.+?)(?=\n\*\*|\Z)"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1).strip() if m else ""


def parse_scenarios(assets_dir: Path) -> list[dict]:
    scenarios = []
    for n in range(1, 21):
        file_a = assets_dir / f"scenario_{n}_party_A.md"
        file_b = assets_dir / f"scenario_{n}_party_B.md"

        if not file_a.exists() or not file_b.exists():
            print(f"  warning: missing files for scenario {n}, skipping")
            continue

        text_a = file_a.read_text()
        text_b = file_b.read_text()

        # Extract title from the section header: ## Scenario N — Title
        title_m = re.search(r"## Scenario \d+ — (.+)", text_a)
        title = title_m.group(1).strip() if title_m else f"Scenario {n}"
        # Strip flags like ⚑
        title = re.sub(r"\s*[⚑⚐]\s*", "", title).strip()

        scenario = {
            "id": f"scenario-{n:03d}",
            "title": title,
            "conflict_type": _extract_field(text_a, "CONFLICT_TYPE"),
            "relationship_context": _extract_field(text_a, "RELATIONSHIP_CONTEXT"),
            "surface_issue": _extract_field(text_a, "SURFACE_ISSUE"),
            "party_a_brief": _extract_field(text_a, "PARTY_A_STAKES"),
            "party_b_brief": _extract_field(text_b, "PARTY_B_STAKES"),
        }
        scenarios.append(scenario)
    return scenarios


def main():
    DATA.mkdir(exist_ok=True)

    print("Parsing personas...")
    personas = parse_personas(ASSETS / "character_personas.md")
    print(f"  found {len(personas)} personas")
    for p in personas:
        missing = [k for k, v in p.items() if not v]
        if missing:
            print(f"  warning: {p['id']} missing fields: {missing}")

    print("Parsing scenarios...")
    scenarios = parse_scenarios(ASSETS)
    print(f"  found {len(scenarios)} scenarios")
    for s in scenarios:
        missing = [k for k, v in s.items() if not v]
        if missing:
            print(f"  warning: {s['id']} ({s['title']}) missing fields: {missing}")

    (DATA / "personas.json").write_text(json.dumps(personas, indent=2, ensure_ascii=False))
    (DATA / "scenarios.json").write_text(json.dumps(scenarios, indent=2, ensure_ascii=False))
    print(f"\nWrote {DATA / 'personas.json'}")
    print(f"Wrote {DATA / 'scenarios.json'}")


if __name__ == "__main__":
    main()
