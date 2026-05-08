"""
VC-04: Gold standard trajectories precede LLM-scaled generation.
Applies to: DEL-005 (Gold standard trajectories)
Tested via: CorpusManager gold count check before silver annotation
"""

import pytest

GOLD_MINIMUM = 10


@pytest.fixture
def corpus_path(tmp_path):
    return str(tmp_path / "corpus.jsonl")


def test_gold_count_meets_minimum(corpus_path):
    """
    Given the corpus JSONL file,
    When counting transcripts with is_gold=True,
    Then the count must be at least 10 before any silver transcripts are present.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"


def test_gold_transcripts_are_fully_annotated(corpus_path):
    """
    Given all gold transcripts in the corpus,
    When inspecting their windows for annotation completeness,
    Then no deficit label field should be null.
    """
    # Arrange
    # Act
    # Assert
    assert False, "Not implemented"
