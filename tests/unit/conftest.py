import pytest
from fpo_mediation.models import DialogueTurn, DialogueWindow, Transcript


def _make_turn(index: int, speaker: str) -> DialogueTurn:
    return {
        "turn_index": index,
        "speaker": speaker,
        "reasoning": f"Reasoning for turn {index}",
        "text": f"Turn {index} spoken text.",
        "director_note": "",
    }


@pytest.fixture
def sample_transcript() -> Transcript:
    return {
        "id": "transcript-001",
        "persona_a_id": "persona-001",
        "persona_b_id": "persona-002",
        "scenario_id": "scenario-001",
        "turns": [_make_turn(i, "party_a" if i % 2 == 0 else "party_b") for i in range(8)],
        "termination_reason": "resolution",
        "is_gold": False,
    }


@pytest.fixture
def sample_window() -> DialogueWindow:
    return {
        "id": "window-001",
        "transcript_id": "transcript-001",
        "window_index": 0,
        "turns": [_make_turn(i, "party_a" if i % 2 == 0 else "party_b") for i in range(7)],
        "acknowledgement_deficit": None,
        "agency_deficit": None,
        "reciprocity_deficit": None,
        "clarity_deficit": None,
        "is_high_friction": False,
        "rationale": None,
        "annotation_source": None,
    }


@pytest.fixture
def sample_gold_transcript() -> Transcript:
    return {
        "id": "transcript-002",
        "persona_a_id": "persona-003",
        "persona_b_id": "persona-004",
        "scenario_id": "scenario-002",
        "turns": [_make_turn(i, "party_a" if i % 2 == 0 else "party_b") for i in range(10)],
        "termination_reason": "impasse",
        "is_gold": True,
    }
