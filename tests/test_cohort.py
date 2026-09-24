"""PATCH 4: C_p^src must exclude the union of every infection window."""
import numpy as np, pandas as pd
import build_cohort as bc


def test_exclusion_mask_covers_both_episodes():
    dates = pd.Series(pd.date_range("2021-01-01", periods=200))
    m = bc.exclusion_mask(dates, ["2021-03-01", "2021-06-01"])
    assert m[dates == pd.Timestamp("2021-03-01")].all()
    assert m[dates == pd.Timestamp("2021-02-08")].all()      # onset - 21
    assert m[dates == pd.Timestamp("2021-03-22")].all()      # onset + 21
    assert not m[dates == pd.Timestamp("2021-02-07")].any()  # just outside
    assert m[dates == pd.Timestamp("2021-06-01")].all()      # second episode
    assert not m[dates == pd.Timestamp("2021-04-20")].any()  # between windows


def test_earlier_infection_window_cannot_enter_calibration_availability():
    """Two episodes. The index event is the earliest with an ONSET date, but an
    earlier ASYMPTOMATIC episode (diagnosis date only) still contaminates the
    negative period and its window must be removed from C_p^src."""
    pid, phase = "P1", "phase1"
    dates = pd.date_range("2020-06-01", periods=400)
    inv = pd.DataFrame({
        "phase": phase, "participant_id": pid, "device": "Fitbit",
        "source_file": "P1_hr.csv", "date": dates.astype(str),
        "night_observed_minutes": 300, "day_observed_minutes": 700,
        "observed_minutes": 1000, "raw_samples": 5000})
    onsets = pd.DataFrame({
        "phase": [phase, phase], "participant_id": [pid, pid],
        "symptomatic": [True, False],
        "onset_date": [pd.Timestamp("2020-09-01"), pd.NaT],
        "diagnosis_date": [pd.NaT, pd.Timestamp("2020-07-01")]})
    dm = pd.DataFrame({"participant_id": [pid], "phase": [phase],
                       "device": ["Fitbit"], "provenance": ["filename_token"],
                       "detail": ["test"]})
    flow, eligible, cal = bc.phase_a(inv, onsets, dm)
    assert eligible == [(phase, pid)]

    index_onset = pd.Timestamp("2020-09-01")                 # earliest with onset
    d = pd.to_datetime(pd.Series(dates))
    before = d < index_onset - pd.Timedelta(days=28)
    anchors = bc.episode_anchors(onsets)
    assert anchors == [pd.Timestamp("2020-07-01"), pd.Timestamp("2020-09-01")]
    excluded = bc.exclusion_mask(d, anchors)
    expected = int((before & ~excluded).sum())
    assert cal[(phase, pid)] == expected
    # the asymptomatic episode's window sits inside the pre-index history
    assert expected < int(before.sum())
    assert int((before & excluded).sum()) == 43              # 21 + 1 + 21 days


def test_single_episode_participant_is_unaffected_by_the_union_logic():
    dates = pd.Series(pd.date_range("2021-01-01", periods=100))
    one = bc.exclusion_mask(dates, ["2021-03-01"])
    two = bc.exclusion_mask(dates, ["2021-03-01", "2021-03-01"])
    assert one.equals(two)


def test_asymptomatic_episode_contributes_an_anchor_via_diagnosis_date():
    rows = pd.DataFrame({"onset_date": [pd.NaT], "diagnosis_date": [pd.Timestamp("2021-02-02")]})
    assert bc.episode_anchors(rows) == [pd.Timestamp("2021-02-02")]


def test_episode_with_neither_date_contributes_no_anchor():
    rows = pd.DataFrame({"onset_date": [pd.NaT], "diagnosis_date": [pd.NaT]})
    assert bc.episode_anchors(rows) == []
