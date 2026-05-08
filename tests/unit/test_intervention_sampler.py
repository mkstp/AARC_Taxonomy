"""
MOD-008: InterventionSampler
Implements: DEL-006
"""

import pytest


@pytest.mark.asyncio
async def test_sample_interventions_returns_correct_count(sample_window, mocker):
    """
    Given a high-friction window and n=6,
    When sample_interventions is called with a mocked OpenAI client,
    Then exactly 6 CandidateIntervention objects are returned.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"


def test_score_intervention_fills_component_scores(sample_window, mocker):
    """
    Given a candidate intervention and its window,
    When score_intervention is called,
    Then all four component score fields are non-null integers.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"


def test_aggregate_score_equals_sum_of_components(sample_window, mocker):
    """
    Given a scored candidate intervention,
    When inspecting aggregate_score,
    Then it must equal the sum of the four component scores.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"


@pytest.mark.asyncio
async def test_sample_only_called_for_high_friction_windows(mocker):
    """
    Given a mix of high- and low-friction windows,
    When sample_batch is called,
    Then sampling is only invoked for windows with is_high_friction=True.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"
