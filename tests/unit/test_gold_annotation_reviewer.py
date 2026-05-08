"""
MOD-005: GoldAnnotationReviewer
Implements: DEL-005
"""

import pytest
from fpo_mediation.gold_annotation_reviewer import (
    load_annotations,
    prompt_labels,
    save_annotation,
)
from fpo_mediation.models import GoldAnnotation


def test_save_and_load_annotation_roundtrip(tmp_path, sample_window):
    """
    Given a gold annotation for a window,
    When saved and reloaded from disk,
    Then the loaded annotation is identical to the original.
    """
    annotation: GoldAnnotation = {
        "window_id": sample_window["id"],
        "acknowledgement_deficit": True,
        "agency_deficit": False,
        "reciprocity_deficit": True,
        "clarity_deficit": False,
        "annotator_notes": "Test note",
        "annotated_by": "test-annotator",
        "annotation_date": "2026-04-23",
    }
    path = str(tmp_path / "annotations.jsonl")

    save_annotation(annotation, path)
    loaded = load_annotations(path)

    assert len(loaded) == 1
    assert loaded[0] == annotation


def test_load_annotations_returns_all_saved(tmp_path, sample_window):
    """
    Given multiple annotations saved to the same path,
    When load_annotations is called,
    Then all saved annotations are returned.
    """
    path = str(tmp_path / "annotations.jsonl")
    for i in range(3):
        annotation: GoldAnnotation = {
            "window_id": f"window-{i:03d}",
            "acknowledgement_deficit": bool(i % 2),
            "agency_deficit": False,
            "reciprocity_deficit": False,
            "clarity_deficit": False,
            "annotator_notes": "",
            "annotated_by": "test-annotator",
            "annotation_date": "2026-04-23",
        }
        save_annotation(annotation, path)

    loaded = load_annotations(path)

    assert len(loaded) == 3
    assert [a["window_id"] for a in loaded] == ["window-000", "window-001", "window-002"]


def test_prompt_labels_rejects_invalid_input(monkeypatch):
    """
    Given simulated invalid user input (not y/n),
    When prompt_labels is called,
    Then it re-prompts rather than accepting the invalid input.
    """
    # First prompt for 'acknowledgement': "x" (invalid), then "y"; remaining: "n"
    responses = iter(["x", "y", "n", "n", "n"])
    monkeypatch.setattr("builtins.input", lambda _: next(responses))

    result = prompt_labels()

    assert result["acknowledgement_deficit"] is True
    assert result["agency_deficit"] is False
    assert result["reciprocity_deficit"] is False
    assert result["clarity_deficit"] is False
