"""
MOD-003: CorpusManager
Implements: DEL-005, DEL-006
"""

import pytest
from fpo_mediation.corpus_manager import (
    get_stats,
    load_all,
    load_transcript,
    mark_gold,
    save_transcript,
)


def test_save_and_load_transcript_roundtrip(tmp_path, sample_transcript):
    """
    Given a transcript object,
    When saved and then loaded from JSONL,
    Then the loaded transcript is identical to the original.
    """
    path = str(tmp_path / "corpus.jsonl")
    save_transcript(sample_transcript, path)
    loaded = load_transcript(sample_transcript["id"], path)
    assert loaded == sample_transcript


def test_load_all_gold_only_filters_correctly(tmp_path, sample_transcript, sample_gold_transcript):
    """
    Given a corpus with both gold and non-gold transcripts,
    When load_all is called with gold_only=True,
    Then only transcripts with is_gold=True are returned.
    """
    path = str(tmp_path / "corpus.jsonl")
    save_transcript(sample_transcript, path)
    save_transcript(sample_gold_transcript, path)

    gold = load_all(path, gold_only=True)
    assert len(gold) == 1
    assert gold[0]["id"] == sample_gold_transcript["id"]


def test_mark_gold_updates_transcript(tmp_path, sample_transcript):
    """
    Given a saved non-gold transcript,
    When mark_gold is called with its ID,
    Then the transcript is_gold field becomes True on reload.
    """
    path = str(tmp_path / "corpus.jsonl")
    save_transcript(sample_transcript, path)
    assert not sample_transcript["is_gold"]

    mark_gold(sample_transcript["id"], path)
    loaded = load_transcript(sample_transcript["id"], path)
    assert loaded["is_gold"] is True


def test_get_stats_returns_expected_keys(tmp_path, sample_transcript):
    """
    Given a corpus with at least one transcript,
    When get_stats is called,
    Then the result contains keys: total, gold_count, avg_turns.
    """
    path = str(tmp_path / "corpus.jsonl")
    save_transcript(sample_transcript, path)

    stats = get_stats(path)
    assert "total" in stats
    assert "gold_count" in stats
    assert "avg_turns" in stats
    assert stats["total"] == 1
    assert stats["gold_count"] == 0
    assert stats["avg_turns"] == len(sample_transcript["turns"])
