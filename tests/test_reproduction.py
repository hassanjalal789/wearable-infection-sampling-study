import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from gate_b_compute import compute_gate_b

RESULT = compute_gate_b()
REPORT = RESULT["report"]
M = RESULT["mishra_detail"]
A = RESULT["alavi_detail"]


def test_mishra_analysed_cases():
    assert M["analysed_cases"] == 32
    assert REPORT["mishra_analysed_cases"]["status"] == "PASS"


def test_mishra_detected_cases():
    assert M["detected_cases_groups_I_II"] == 26
    assert REPORT["mishra_detected"]["status"] == "PASS"


def test_mishra_symptom_denominator_and_at_or_before():
    assert M["symptom_information_cases_among_detected"] == 25
    assert M["detected_at_or_before_onset"] == 22
    assert REPORT["mishra_detected_at_or_before_onset_of_25"]["status"] == "PASS"


def test_mishra_median_lead():
    assert M["median_lead_days_vs_onset"] == 4.0
    assert REPORT["mishra_median_lead_days_vs_onset"]["status"] == "PASS"


def test_alavi_positive_cohort_structure():
    assert A["confirmed_positives"] == 84
    assert A["symptomatic_rows"] == 66
    assert A["asymptomatic_rows"] == 18
    assert A["fig4_union_matches_positive_cohort"] is True
    assert A["duplicate_alert_ids"] == []
    assert REPORT["alavi_confirmed_positives"]["status"] == "PASS"


def test_alavi_sensitivity():
    assert A["symptomatic_at_or_before_onset"] == 53
    assert A["asymptomatic_at_or_before_test"] == 14
    assert A["true_positive_participants"] == 67
    assert abs(A["sensitivity_per_person_pct"] - (100.0 * 67 / 84)) < 1e-12
    assert REPORT["alavi_sensitivity_per_person_pct"]["status"] == "PASS"


def test_alavi_specificity_public_data_limitation_is_explicit():
    s = REPORT["alavi_specificity_per_alert_day_pct"]
    assert s["status"] == "NOT_RECONSTRUCTIBLE_PUBLIC_DATA"
    assert s["published_numerator_TN"] == 87124
    assert s["published_false_positive_alert_days"] == 12186
