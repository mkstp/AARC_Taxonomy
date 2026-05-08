"""
Integration: Preference pair pipeline
InterventionSampler → PreferencePairGenerator
"""

import pytest


@pytest.mark.asyncio
async def test_high_friction_windows_yield_pairs(sample_window, mocker):
    """
    Given a high-friction annotated window,
    When interventions are sampled, scored, and ranked,
    Then at least one preference pair is produced.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"


def test_preference_pairs_satisfy_bradley_terry_format(sample_window, mocker):
    """
    Given generated preference pairs,
    When inspecting pair structure,
    Then each pair contains chosen_text, rejected_text, and score_gap > 0.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"
