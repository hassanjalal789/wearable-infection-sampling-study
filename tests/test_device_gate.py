"""Final patch, audit item 1: the device gate is scoped to infection candidates."""
import pandas as pd, pytest
import check_device_coverage as cdc


def dm(rows):
    return pd.DataFrame(rows, columns=["participant_id", "phase", "device",
                                       "provenance", "detail"])


def onsets(ids):
    return pd.DataFrame({"phase": [p for p, _ in ids],
                         "participant_id": [i for _, i in ids],
                         "symptomatic": [True] * len(ids),
                         "onset_date": ["2021-01-01"] * len(ids)})


def test_unknown_non_candidates_do_not_block():
    """Thousands of Phase 1 archive participants lack device tokens; if they are
    not infection candidates they must not abort the pipeline."""
    d = dm([("A", "phase1", "Fitbit", "supplementary_table", "t1")]
           + [(f"N{i}", "phase1", "UNKNOWN", "UNKNOWN", "no token") for i in range(500)])
    r = cdc.report(d, onsets([("phase1", "A")]))
    assert r["blocking"] is False
    assert r["candidates_unresolved"] == 0
    assert r["total_unknown_or_conflict_all_participants"] == 500   # still reported


def test_unknown_candidate_blocks():
    d = dm([("A", "phase1", "UNKNOWN", "UNKNOWN", "no token"),
            ("N1", "phase1", "UNKNOWN", "UNKNOWN", "no token")])
    r = cdc.report(d, onsets([("phase1", "A")]))
    assert r["blocking"] is True and r["candidates_unresolved"] == 1
    assert any("phase1:A" in x for x in r["unresolved_candidate_ids"])


def test_conflicting_candidate_blocks():
    d = dm([("A", "phase1", "CONFLICT", "UNKNOWN", "two tokens")])
    r = cdc.report(d, onsets([("phase1", "A")]))
    assert r["blocking"] is True


def test_candidate_absent_from_device_map_blocks():
    d = dm([("N1", "phase1", "Fitbit", "filename_token", "t")])
    r = cdc.report(d, onsets([("phase1", "A")]))
    assert r["blocking"] is True
    assert r["n_candidates_absent_from_device_map"] == 1


def test_all_candidates_resolved_passes_and_still_reports_totals():
    d = dm([("A", "phase1", "Fitbit", "supplementary_table", "t1"),
            ("B", "phase2", "AppleWatch", "filename_token", "t2"),
            ("N1", "phase1", "UNKNOWN", "UNKNOWN", "no token")])
    r = cdc.report(d, onsets([("phase1", "A"), ("phase2", "B")]))
    assert r["blocking"] is False
    assert r["candidates_resolved"] == 2
    assert r["total_unknown_or_conflict_all_participants"] == 1


def test_candidate_scope_includes_cases_that_later_drop_out():
    """A candidate excluded later for a missing baseline still needs a device, so
    the flow table can say WHY they dropped rather than conflating reasons."""
    d = dm([("A", "phase1", "Fitbit", "supplementary_table", "t"),
            ("B", "phase1", "UNKNOWN", "UNKNOWN", "no token")])
    r = cdc.report(d, onsets([("phase1", "A"), ("phase1", "B")]))
    assert r["blocking"] is True and r["n_candidates"] == 2
