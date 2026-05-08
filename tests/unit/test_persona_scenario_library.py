"""
MOD-001: PersonaScenarioLibrary
Implements: DEL-005, DEL-006
"""

import json
import pytest

from fpo_mediation.persona_scenario_library import (
    get_all_pairs,
    load_personas,
    load_scenarios,
    load_stylistics_profiles,
    sample_pair,
    sample_stylistics,
)


def test_load_personas_returns_list(tmp_path, sample_persona_a, sample_persona_b):
    """
    Given a valid personas JSON file,
    When load_personas is called,
    Then a list of Persona objects is returned.
    """
    path = tmp_path / "personas.json"
    path.write_text(json.dumps([sample_persona_a, sample_persona_b]))

    result = load_personas(str(path))

    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0]["id"] == sample_persona_a["id"]


def test_load_scenarios_returns_list(tmp_path, sample_scenario):
    """
    Given a valid scenarios JSON file,
    When load_scenarios is called,
    Then a list of Scenario objects is returned.
    """
    path = tmp_path / "scenarios.json"
    path.write_text(json.dumps([sample_scenario]))

    result = load_scenarios(str(path))

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == sample_scenario["id"]


def test_sample_pair_returns_two_distinct_personas(sample_persona_a, sample_persona_b, sample_scenario):
    """
    Given a persona list and scenario list,
    When sample_pair is called,
    Then the two returned personas must have distinct IDs.
    """
    personas = [sample_persona_a, sample_persona_b]
    scenarios = [sample_scenario]

    a, b, scenario = sample_pair(personas, scenarios)

    assert a["id"] != b["id"]
    assert scenario["id"] == sample_scenario["id"]


def test_sample_pair_is_reproducible_with_seed(sample_persona_a, sample_persona_b, sample_scenario):
    """
    Given the same seed value,
    When sample_pair is called twice,
    Then both calls return identical persona-scenario tuples.
    """
    personas = [sample_persona_a, sample_persona_b]
    scenarios = [sample_scenario]

    result_1 = sample_pair(personas, scenarios, seed=42)
    result_2 = sample_pair(personas, scenarios, seed=42)

    assert result_1[0]["id"] == result_2[0]["id"]
    assert result_1[1]["id"] == result_2[1]["id"]
    assert result_1[2]["id"] == result_2[2]["id"]


def test_load_stylistics_profiles_returns_list(tmp_path, sample_stylistics_profile):
    """
    Given a valid stylistics_profiles JSON file,
    When load_stylistics_profiles is called,
    Then a list of StylisticsProfile objects is returned.
    """
    path = tmp_path / "stylistics_profiles.json"
    path.write_text(json.dumps([sample_stylistics_profile]))

    result = load_stylistics_profiles(str(path))

    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0]["id"] == sample_stylistics_profile["id"]


def test_sample_stylistics_returns_two_profiles(sample_stylistics_profile):
    """
    Given a list with one profile,
    When sample_stylistics is called,
    Then two profiles are returned (same profile is allowed for both slots).
    """
    profiles = [sample_stylistics_profile]

    a, b = sample_stylistics(profiles)

    assert a["id"] == sample_stylistics_profile["id"]
    assert b["id"] == sample_stylistics_profile["id"]


def test_sample_stylistics_is_reproducible_with_seed(sample_stylistics_profile):
    """
    Given the same seed value and two profiles,
    When sample_stylistics is called twice,
    Then both calls return identical profile pairs.
    """
    second = {**sample_stylistics_profile, "id": "stylistics-002"}
    profiles = [sample_stylistics_profile, second]

    result_1 = sample_stylistics(profiles, seed=42)
    result_2 = sample_stylistics(profiles, seed=42)

    assert result_1[0]["id"] == result_2[0]["id"]
    assert result_1[1]["id"] == result_2[1]["id"]


def test_sample_stylistics_allows_same_profile_for_both(sample_stylistics_profile):
    """
    Given a single profile,
    When sample_stylistics is called,
    Then both returned profiles may share the same ID (no uniqueness constraint).
    """
    profiles = [sample_stylistics_profile]

    a, b = sample_stylistics(profiles)

    assert a["id"] == b["id"]
