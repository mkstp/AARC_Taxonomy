"""Shared fixtures for the FPO mediation pipeline test suite."""

import pytest


# --- Persona / Scenario fixtures ---

@pytest.fixture
def sample_persona_a():
    return {
        "id": "persona-001",
        "name": "Alex",
        "core_needs": "To be heard and taken seriously",
        "beliefs_about_self": "Competent but undervalued",
        "beliefs_about_others": "Others tend to dismiss my concerns",
        "tki_primary_mode": "competing",
        "storm_shift": "Escalates tone, repeats core concern",
        "activation_profile": "Activates quickly; slow to de-escalate without acknowledgment",
        "repair_orientation": "Responds to direct acknowledgment of their concerns",
        "face_salience": "High; concession feels like defeat",
        "communicative_register": "Direct and assertive; minimal hedging",
    }


@pytest.fixture
def sample_persona_b():
    return {
        "id": "persona-002",
        "name": "Jordan",
        "core_needs": "To maintain control of the process",
        "beliefs_about_self": "Rational and fair",
        "beliefs_about_others": "Others are often emotional and unproductive",
        "tki_primary_mode": "avoiding",
        "storm_shift": "Becomes procedural and dismissive",
        "activation_profile": "Slow to activate; disengages rather than escalates",
        "repair_orientation": "Responds to procedural de-escalation and clear agreements",
        "face_salience": "Low; can concede without loss of standing",
        "communicative_register": "Formal and measured; prefers process over emotion",
    }


@pytest.fixture
def sample_scenario():
    return {
        "id": "scenario-001",
        "conflict_type": "workplace",
        "relationship_context": "Peers with power asymmetry; Alex reports to Jordan's team",
        "surface_issue": "Credit for a shared project deliverable",
        "party_a_brief": "Professional recognition and career advancement",
        "party_b_brief": "Team cohesion and maintaining authority",
    }


# --- Dialogue turn and transcript fixtures ---

@pytest.fixture
def sample_turns():
    return [
        {
            "turn_index": i,
            "speaker": "party_a" if i % 2 == 0 else "party_b",
            "reasoning": f"Reasoning for turn {i}",
            "text": f"Turn {i} text.",
            "director_note": "",
        }
        for i in range(8)
    ]


@pytest.fixture
def sample_transcript(sample_turns):
    return {
        "id": "transcript-001",
        "persona_a_id": "persona-001",
        "persona_b_id": "persona-002",
        "scenario_id": "scenario-001",
        "turns": sample_turns,
        "termination_reason": "impasse",
        "is_gold": False
    }


@pytest.fixture
def sample_gold_transcript(sample_transcript):
    t = sample_transcript.copy()
    t["id"] = "transcript-gold-001"
    t["is_gold"] = True
    return t


# --- Window fixtures ---

@pytest.fixture
def sample_window(sample_turns):
    return {
        "id": "window-001",
        "transcript_id": "transcript-001",
        "window_index": 0,
        "turns": sample_turns[:7],
        "acknowledgement_deficit": True,
        "agency_deficit": False,
        "reciprocity_deficit": False,
        "clarity_deficit": False,
        "is_high_friction": True,
        "rationale": "Repeated dismissal pattern across turns 0-6",
        "annotation_source": "gold"
    }


@pytest.fixture
def unannotated_window(sample_turns):
    return {
        "id": "window-002",
        "transcript_id": "transcript-001",
        "window_index": 1,
        "turns": sample_turns[1:8],
        "acknowledgement_deficit": None,
        "agency_deficit": None,
        "reciprocity_deficit": None,
        "clarity_deficit": None,
        "is_high_friction": False,
        "rationale": None,
        "annotation_source": None
    }


# --- Intervention and preference pair fixtures ---

@pytest.fixture
def sample_intervention_group(sample_window):
    candidates = [
        {
            "id": f"intervention-00{i}",
            "window_id": "window-001",
            "intervention_type": "reflective_paraphrasing",
            "text": f"Intervention {i} text",
            "acknowledgement_score": 3 - i,
            "agency_score": 1,
            "reciprocity_score": 1,
            "clarity_score": 1,
            "aggregate_score": 6 - i
        }
        for i in range(4)
    ]
    return {"window_id": "window-001", "candidates": candidates}


@pytest.fixture
def sample_preference_pair():
    return {
        "id": "pair-001",
        "window_id": "window-001",
        "chosen_id": "intervention-000",
        "rejected_id": "intervention-003",
        "chosen_text": "Intervention 0 text",
        "rejected_text": "Intervention 3 text",
        "score_gap": 3,
        "annotator_rationale": "Chosen directly addresses acknowledgement deficit"
    }


@pytest.fixture
def sample_stylistics_profile():
    return {
        "id": "stylistics-001",
        "label": "Low-context direct",
        "silence_pause_style": "Silence is uncomfortable; you fill pauses quickly.",
        "filler_style": "Low frequency; occasional 'uh' or 'um'.",
        "turn_taking_style": "Wait for a clear pause before speaking.",
        "redundancy_style": "Low hedging and low repetition; you state a point once and move on.",
    }


# --- Markers ---

def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with -m 'not slow')")
    config.addinivalue_line("markers", "live_api: marks tests that make live API calls")
