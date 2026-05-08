"""MOD-001: PersonaScenarioLibrary — Implements DEL-005, DEL-006. Validated by VC-04."""

import json
import random

from .models import Persona, Scenario, StylisticsProfile


def load_personas(path: str) -> list[Persona]:
    with open(path) as f:
        return json.load(f)


def load_scenarios(path: str) -> list[Scenario]:
    with open(path) as f:
        return json.load(f)


def sample_pair(
    personas: list[Persona],
    scenarios: list[Scenario],
    seed: int | None = None,
) -> tuple[Persona, Persona, Scenario]:
    rng = random.Random(seed)
    a, b = rng.sample(personas, 2)
    scenario = rng.choice(scenarios)
    return a, b, scenario


def load_stylistics_profiles(path: str) -> list[StylisticsProfile]:
    with open(path) as f:
        return json.load(f)


def sample_stylistics(
    profiles: list[StylisticsProfile],
    seed: int | None = None,
) -> tuple[StylisticsProfile, StylisticsProfile]:
    rng = random.Random(seed)
    return rng.choice(profiles), rng.choice(profiles)


def get_all_pairs(
    personas: list[Persona],
    scenarios: list[Scenario],
) -> list[tuple[Persona, Persona, Scenario]]:
    return [
        (a, b, scenario)
        for i, a in enumerate(personas)
        for j, b in enumerate(personas)
        if i != j
        for scenario in scenarios
    ]
