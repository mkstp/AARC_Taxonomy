"""
Unit tests for scripts/iaa.py — inter-annotator agreement metrics.
Covers cohen_kappa, krippendorff_alpha, interpret_kappa, compute, and render_analysis.
"""

import sys
import math
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))
from iaa import cohen_kappa, krippendorff_alpha, interpret_kappa, compute, render_analysis, COMPONENTS


# ---------------------------------------------------------------------------
# cohen_kappa
# ---------------------------------------------------------------------------

class TestCohenKappa:

    def test_perfect_agreement_returns_one(self):
        """
        Given two annotators with identical binary labels,
        When cohen_kappa is called,
        Then it returns 1.0.
        """
        h = [1, 0, 1, 0, 1]
        l = [1, 0, 1, 0, 1]
        assert cohen_kappa(h, l) == pytest.approx(1.0)

    def test_complete_disagreement_balanced_returns_negative_one(self):
        """
        Given two annotators with perfectly inverted balanced labels,
        When cohen_kappa is called,
        Then it returns -1.0.
        """
        h = [1, 0, 1, 0]
        l = [0, 1, 0, 1]
        assert cohen_kappa(h, l) == pytest.approx(-1.0)

    def test_chance_agreement_returns_zero(self):
        """
        Given labels where observed agreement equals expected chance agreement,
        When cohen_kappa is called,
        Then it returns 0.0.
        """
        # Both annotators label 50% positive; observed agreement = 50% = Pe
        h = [1, 1, 0, 0]
        l = [1, 0, 1, 0]
        assert cohen_kappa(h, l) == pytest.approx(0.0)

    def test_all_negative_labels_returns_one(self):
        """
        Given both annotators label all turns negative (Pe == 1),
        When cohen_kappa is called,
        Then it returns 1.0 without dividing by zero.
        """
        h = [0, 0, 0, 0]
        l = [0, 0, 0, 0]
        assert cohen_kappa(h, l) == pytest.approx(1.0)

    def test_known_moderate_agreement(self):
        """
        Given labels with known kappa of ~0.524 (equal marginals, 80% observed agreement),
        When cohen_kappa is called,
        Then it returns the expected value within tolerance.
        """
        h = [1, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        l = [1, 0, 1, 0, 0, 0, 0, 0, 1, 0]
        # Po=0.8, p_h=p_l=0.3, Pe=0.58 → κ = 0.22/0.42
        assert cohen_kappa(h, l) == pytest.approx(0.22 / 0.42, rel=1e-4)

    def test_asymmetric_marginals_differs_from_symmetric(self):
        """
        Given annotators with different positive rates (0.3 vs 0.2),
        When cohen_kappa is called,
        Then kappa differs from krippendorff_alpha due to marginal handling.
        """
        h = [1, 1, 1, 0, 0, 0, 0, 0, 0, 0]
        l = [1, 1, 0, 0, 0, 0, 0, 0, 0, 0]
        k = cohen_kappa(h, l)
        a = krippendorff_alpha(h, l)
        assert k != pytest.approx(a, rel=1e-3)


# ---------------------------------------------------------------------------
# krippendorff_alpha
# ---------------------------------------------------------------------------

class TestKrippendorffAlpha:

    def test_perfect_agreement_returns_one(self):
        """
        Given two annotators with identical binary labels,
        When krippendorff_alpha is called,
        Then it returns 1.0.
        """
        h = [1, 0, 1, 0, 1]
        l = [1, 0, 1, 0, 1]
        assert krippendorff_alpha(h, l) == pytest.approx(1.0)

    def test_complete_disagreement_balanced_returns_negative_one(self):
        """
        Given two annotators with perfectly inverted balanced labels,
        When krippendorff_alpha is called,
        Then it returns -1.0.
        """
        h = [1, 0, 1, 0]
        l = [0, 1, 0, 1]
        assert krippendorff_alpha(h, l) == pytest.approx(-1.0)

    def test_chance_level_agreement_returns_zero(self):
        """
        Given labels at chance agreement (Do == De),
        When krippendorff_alpha is called,
        Then it returns 0.0.
        """
        # Both 50% positive, 50% observed agreement → Do=De=0.5
        h = [1, 1, 0, 0]
        l = [1, 0, 1, 0]
        assert krippendorff_alpha(h, l) == pytest.approx(0.0)

    def test_all_same_class_no_division_by_zero(self):
        """
        Given all labels are negative (De == 0, no variation),
        When krippendorff_alpha is called,
        Then it returns 1.0 without raising ZeroDivisionError.
        """
        h = [0, 0, 0, 0]
        l = [0, 0, 0, 0]
        assert krippendorff_alpha(h, l) == pytest.approx(1.0)

    def test_known_moderate_agreement_equal_marginals(self):
        """
        Given equal annotator marginals, alpha equals kappa (mathematical identity for 2 annotators).
        When both metrics are computed,
        Then their values are equal within floating-point tolerance.
        """
        h = [1, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        l = [1, 0, 1, 0, 0, 0, 0, 0, 1, 0]
        assert krippendorff_alpha(h, l) == pytest.approx(cohen_kappa(h, l), rel=1e-6)

    def test_asymmetric_marginals_alpha_lower_than_kappa(self):
        """
        Given annotators with different positive rates (LLM over-labels),
        When both metrics are computed,
        Then alpha is lower than kappa because pooled marginals raise De.
        """
        # h positive rate = 0.3, l positive rate = 0.5 (LLM over-labels)
        h = [1, 0, 1, 0, 0, 0, 0, 0, 1, 0]
        l = [1, 1, 1, 0, 0, 0, 1, 0, 1, 0]
        k = cohen_kappa(h, l)
        a = krippendorff_alpha(h, l)
        assert a < k


# ---------------------------------------------------------------------------
# interpret_kappa
# ---------------------------------------------------------------------------

class TestInterpretKappa:

    @pytest.mark.parametrize("k,expected", [
        (-0.1,  "worse than chance"),
        (0.0,   "slight"),
        (0.10,  "slight"),
        (0.20,  "fair"),
        (0.39,  "fair"),
        (0.40,  "moderate"),
        (0.59,  "moderate"),
        (0.60,  "substantial"),
        (0.79,  "substantial"),
        (0.80,  "almost perfect"),
        (1.00,  "almost perfect"),
    ])
    def test_boundary_values(self, k, expected):
        """
        Given a kappa value at each boundary,
        When interpret_kappa is called,
        Then it returns the correct Landis-Koch label.
        """
        assert interpret_kappa(k) == expected


# ---------------------------------------------------------------------------
# compute
# ---------------------------------------------------------------------------

class TestCompute:

    def _make_annotation(self, turn_id, a=False, g=False, r=False, c=False):
        return {
            "turn_id": turn_id,
            "acknowledgement_deficit": a,
            "agency_deficit": g,
            "reciprocity_deficit": r,
            "clarity_deficit": c,
        }

    def test_returns_result_for_each_component(self):
        """
        Given matching human and LLM annotations for two turns,
        When compute is called,
        Then the result contains an entry for each of the four AARC components.
        """
        human = {
            "t1": self._make_annotation("t1", a=True),
            "t2": self._make_annotation("t2"),
        }
        llm = {
            "t1": self._make_annotation("t1", a=True),
            "t2": self._make_annotation("t2"),
        }
        result = compute(human, llm, {"t1", "t2"})
        assert set(result.keys()) == set(COMPONENTS)

    def test_perfect_agreement_yields_kappa_one(self):
        """
        Given human and LLM annotations that are identical across all turns,
        When compute is called,
        Then cohen_kappa is 1.0 for all components.
        """
        human = {f"t{i}": self._make_annotation(f"t{i}", a=bool(i % 2)) for i in range(6)}
        llm = {f"t{i}": self._make_annotation(f"t{i}", a=bool(i % 2)) for i in range(6)}
        result = compute(human, llm, set(human.keys()))
        assert result["acknowledgement_deficit"]["cohen_kappa"] == pytest.approx(1.0)

    def test_observed_agreement_is_between_zero_and_one(self):
        """
        Given any valid annotations,
        When compute is called,
        Then observed_agreement for each component is in [0, 1].
        """
        human = {
            "t1": self._make_annotation("t1", a=True, g=False),
            "t2": self._make_annotation("t2", a=False, g=True),
            "t3": self._make_annotation("t3", a=True, g=True),
        }
        llm = {
            "t1": self._make_annotation("t1", a=False, g=False),
            "t2": self._make_annotation("t2", a=False, g=False),
            "t3": self._make_annotation("t3", a=True, g=True),
        }
        result = compute(human, llm, set(human.keys()))
        for comp in COMPONENTS:
            assert 0.0 <= result[comp]["observed_agreement"] <= 1.0

    def test_result_includes_all_required_keys(self):
        """
        Given valid annotations,
        When compute is called,
        Then each component result contains the five expected metric keys.
        """
        human = {"t1": self._make_annotation("t1")}
        llm = {"t1": self._make_annotation("t1")}
        result = compute(human, llm, {"t1"})
        expected_keys = {"n", "observed_agreement", "human_positive_rate", "llm_positive_rate",
                         "cohen_kappa", "krippendorff_alpha"}
        for comp in COMPONENTS:
            assert set(result[comp].keys()) == expected_keys

    def test_only_matched_turns_are_used(self):
        """
        Given human annotations for 4 turns but only 2 matched by LLM,
        When compute is called with those 2 as common_ids,
        Then n equals 2 for all components.
        """
        human = {f"t{i}": self._make_annotation(f"t{i}") for i in range(4)}
        llm = {f"t{i}": self._make_annotation(f"t{i}") for i in range(2)}
        result = compute(human, llm, {"t0", "t1"})
        for comp in COMPONENTS:
            assert result[comp]["n"] == 2


# ---------------------------------------------------------------------------
# render_analysis
# ---------------------------------------------------------------------------

class TestRenderAnalysis:

    def _minimal_results(self, kappa=0.6, alpha=0.6, po=0.9, h_pos=0.15, l_pos=0.15):
        return {
            comp: {
                "n": 56,
                "cohen_kappa": kappa,
                "krippendorff_alpha": alpha,
                "observed_agreement": po,
                "human_positive_rate": h_pos,
                "llm_positive_rate": l_pos,
            }
            for comp in COMPONENTS
        }

    def test_output_contains_all_four_component_labels(self):
        """
        Given valid results for all components,
        When render_analysis is called,
        Then the output contains the display label for each AARC component.
        """
        results = self._minimal_results()
        output = render_analysis(results, 56, 56, 100)
        for label in ["Acknowledgement", "Agency", "Reciprocity", "Clarity"]:
            assert label in output

    def test_output_contains_required_sections(self):
        """
        Given valid results,
        When render_analysis is called,
        Then the output contains the Analysis, Limitations, and Results sections.
        """
        results = self._minimal_results()
        output = render_analysis(results, 56, 56, 100)
        for section in ["## Analysis", "### Limitations", "## Results"]:
            assert section in output

    def test_llm_over_labeling_flagged_in_output(self):
        """
        Given LLM positive rate substantially higher than human positive rate,
        When render_analysis is called,
        Then the output notes that the model may be over-sensitive.
        """
        results = self._minimal_results(h_pos=0.10, l_pos=0.30)
        output = render_analysis(results, 56, 56, 100)
        assert "over-sensitive" in output

    def test_llm_under_labeling_flagged_in_output(self):
        """
        Given LLM positive rate substantially lower than human positive rate,
        When render_analysis is called,
        Then the output notes that the model may be under-sensitive.
        """
        results = self._minimal_results(h_pos=0.30, l_pos=0.10)
        output = render_analysis(results, 56, 56, 100)
        assert "under-sensitive" in output

    def test_low_prevalence_triggers_kappa_paradox_warning(self):
        """
        Given a human positive rate below 10% for at least one component,
        When render_analysis is called,
        Then the output includes a prevalence paradox caveat.
        """
        results = self._minimal_results(h_pos=0.05)
        output = render_analysis(results, 56, 56, 100)
        assert "prevalence paradox" in output

    def test_returns_non_empty_string(self):
        """
        Given valid inputs,
        When render_analysis is called,
        Then it returns a non-empty string without raising.
        """
        results = self._minimal_results()
        output = render_analysis(results, 56, 56, 100)
        assert isinstance(output, str) and len(output) > 0
