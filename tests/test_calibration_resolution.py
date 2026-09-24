from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import calibration_resolution as cr


def test_choose_c_min_explicit_fallback_reporting():
    rule = cr.choose_c_min([28, 28, 28, 0])
    assert rule["chosen_C_min"] == 28
    assert rule["fallback_invoked"] is True
    assert rule["fallback_value"] == 28
    assert rule["retention_floor_met"] is False
    assert rule["retention_at_choice"] == 0.75
    assert "fallback C_min=28 was invoked" in rule["note"]


def test_choose_c_min_nonfallback_reporting():
    rule = cr.choose_c_min([42, 42, 42, 42, 28])
    assert rule["chosen_C_min"] == 42
    assert rule["fallback_invoked"] is False
    assert rule["fallback_value"] == 28
    assert rule["retention_floor_met"] is True
    assert rule["retention_at_choice"] == 0.8
    assert "highest admissible candidate selected" in rule["note"]
