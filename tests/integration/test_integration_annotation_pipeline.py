"""
Integration: Annotation pipeline
WindowExtractor → DSPyAnnotator → ConsistencyFilter
"""

import pytest


def test_windows_extracted_and_annotated(sample_transcript, mocker):
    """
    Given a transcript,
    When windows are extracted and annotated by the DSPy module,
    Then all windows have non-null deficit labels.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"


def test_consistency_filter_applied_after_annotation(sample_transcript, mocker):
    """
    Given annotated silver windows and gold annotations,
    When the full annotation pipeline runs,
    Then only windows passing the consistency filter remain in the corpus.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"
