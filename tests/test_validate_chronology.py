"""Tests for the chronology validator.

The synthetic fixtures below are deliberately wrong in one way each, and every
test checks that the validator rejects them for that reason and no other. One
fixture adds a genuine later analysis with its own records and must pass
without changing the completed primary analysis. The last test runs the
validator on this repository's own published chronology.
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import validate_chronology as vc

REPO = Path(__file__).resolve().parents[1]
WORDING = "Primary analysis completed by 4 September 2026. Release began on 19 September 2026."


def _write(root: Path, rel: str, text: str = "record\n") -> str:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    return rel


def _base(root: Path) -> dict:
    """A small, fully supported synthetic chronology."""
    _write(root, "README.md", f"# Study\n\n{WORDING}\n")
    _write(root, "docs/NOTES.md", f"{WORDING}\n")
    for rel in ("docs/protocol.md", "docs/amendment.md", "docs/post_primary.md",
                "results/run/manifest.json", "CHANGELOG.md"):
        _write(root, rel)
    return {
        "timezone": "Asia/Karachi",
        "required_wording": {"text": WORDING, "files": ["README.md", "docs/NOTES.md"]},
        "claim_documents": ["README.md", "docs/NOTES.md"],
        "events": [
            {"id": "P", "type": "protocol", "date": "2026-08-31", "status": "historical",
             "sources": ["docs/protocol.md"]},
            {"id": "RUN", "type": "execution", "start": "2026-09-02", "end": "2026-09-04",
             "status": "historical", "run_id": "run", "data_kind": "real",
             "authoritative_run": True, "sources": ["results/run/manifest.json"]},
            {"id": "POST", "type": "protocol_amendment", "date": "2026-09-04",
             "status": "historical", "records_primary_outcomes_known": True,
             "sources": ["docs/post_primary.md"]},
            {"id": "PRIMARY", "type": "analysis_milestone", "anchor": "primary_analysis_completed",
             "date": "2026-09-04", "status": "completed", "sources": ["docs/post_primary.md"]},
            {"id": "RELEASE", "type": "publication_phase", "start": "2026-09-19",
             "status": "active", "sources": ["CHANGELOG.md"]},
            {"id": "TARGET", "type": "target", "target_date": "2026-09-28", "status": "planned",
             "completion_phrases": ["package is complete"]},
        ],
        "ordering": [["P", "RUN"], ["RUN", "POST"], ["PRIMARY", "RELEASE"], ["RELEASE", "TARGET"]],
        "additional_analyses": [],
    }


def _codes(findings):
    return sorted({f.code for f in findings})


def _event(facts, eid):
    return next(e for e in facts["events"] if e["id"] == eid)


def test_supported_synthetic_chronology_passes(tmp_path):
    assert vc.validate(tmp_path, _base(tmp_path)) == []


def test_unsupported_start_date_is_rejected(tmp_path):
    facts = _base(tmp_path)
    facts["events"].insert(0, {"id": "START", "type": "research_start", "date": "2026-06-01",
                               "status": "historical", "sources": []})
    assert _codes(vc.validate(tmp_path, facts)) == ["unsupported_claim"]


def test_target_mislabelled_completed_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _event(facts, "TARGET")["status"] = "completed"
    assert _codes(vc.validate(tmp_path, facts)) == ["target_completed_without_evidence"]


def test_completion_claim_in_a_document_contradicts_a_planned_target(tmp_path):
    facts = _base(tmp_path)
    _write(tmp_path, "README.md", f"# Study\n\n{WORDING}\n\nThe package is complete.\n")
    assert _codes(vc.validate(tmp_path, facts)) == ["completion_claim_contradicts_status"]


def test_missing_source_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _event(facts, "P")["sources"] = ["docs/not_there.md"]
    assert _codes(vc.validate(tmp_path, facts)) == ["missing_source"]


def test_source_outside_the_repository_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _event(facts, "P")["sources"] = ["../outside.md"]
    assert _codes(vc.validate(tmp_path, facts)) == ["missing_source"]


def test_additional_analysis_without_execution_evidence_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _write(tmp_path, "analyses/extra/plan.md")
    facts["additional_analyses"] = [{
        "id": "EXTRA", "question": "a later question", "status": "active",
        "start": "2026-09-25", "plan": "analyses/extra/plan.md",
        "execution_evidence": [], "results": [], "modifies_events": [],
    }]
    assert _codes(vc.validate(tmp_path, facts)) == ["additional_analysis_without_execution_evidence"]


def test_genuine_later_analysis_passes_without_changing_the_primary(tmp_path):
    facts = _base(tmp_path)
    before = copy.deepcopy(_event(facts, "PRIMARY"))
    for rel in ("analyses/extra/plan.md", "analyses/extra/run_log.md", "analyses/extra/results.csv"):
        _write(tmp_path, rel)
    facts["additional_analyses"] = [{
        "id": "EXTRA", "question": "a later question", "status": "completed",
        "start": "2026-09-25T09:00:00+05:00", "plan": "analyses/extra/plan.md",
        "execution_evidence": ["analyses/extra/run_log.md"],
        "results": ["analyses/extra/results.csv"], "modifies_events": [],
    }]
    assert vc.validate(tmp_path, facts) == []
    assert _event(facts, "PRIMARY") == before


def test_additional_analysis_may_not_modify_the_primary(tmp_path):
    facts = _base(tmp_path)
    for rel in ("analyses/extra/plan.md", "analyses/extra/run_log.md", "analyses/extra/results.csv"):
        _write(tmp_path, rel)
    facts["additional_analyses"] = [{
        "id": "EXTRA", "status": "completed", "plan": "analyses/extra/plan.md",
        "execution_evidence": ["analyses/extra/run_log.md"],
        "results": ["analyses/extra/results.csv"], "modifies_events": ["PRIMARY"],
    }]
    assert _codes(vc.validate(tmp_path, facts)) == ["additional_analysis_modifies_primary"]


def test_primary_dated_after_outcomes_were_known_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _event(facts, "PRIMARY")["date"] = "2026-09-10"
    assert _codes(vc.validate(tmp_path, facts)) == ["primary_after_outcomes_known"]


def test_real_run_relabelled_as_setup_output_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _event(facts, "RUN")["data_kind"] = "dummy"
    assert _codes(vc.validate(tmp_path, facts)) == ["relabelled_real_run"]


def test_relabelling_with_correction_evidence_is_not_flagged(tmp_path):
    facts = _base(tmp_path)
    _write(tmp_path, "docs/correction.md")
    ev = _event(facts, "RUN")
    ev["data_kind"] = "dummy"
    ev["correction_evidence"] = ["docs/correction.md"]
    assert vc.validate(tmp_path, facts) == []


def test_missing_required_wording_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _write(tmp_path, "docs/NOTES.md", "Some other text.\n")
    assert _codes(vc.validate(tmp_path, facts)) == ["required_wording_missing"]


def test_ordering_violation_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _event(facts, "P")["date"] = "2026-09-05"
    assert _codes(vc.validate(tmp_path, facts)) == ["ordering_violation"]


def test_invalid_status_is_rejected(tmp_path):
    facts = _base(tmp_path)
    _event(facts, "P")["status"] = "done"
    assert _codes(vc.validate(tmp_path, facts)) == ["invalid_status"]


@pytest.mark.parametrize("value", ["04/09/2026", "2026-9-4", "4 September 2026", "2026-09-04T10:00:00"])
def test_ambiguous_or_inconsistent_date_formats_are_rejected(tmp_path, value):
    facts = _base(tmp_path)
    _event(facts, "P")["date"] = value
    assert _codes(vc.validate(tmp_path, facts)) == ["invalid_date_format"]


def test_timestamps_convert_to_the_stated_zone_without_moving_across_weeks():
    assert str(vc.parse_day("2026-09-03T21:30:00Z", "Asia/Karachi")) == "2026-09-04"
    assert str(vc.parse_day("2026-09-03T18:59:00Z", "Asia/Karachi")) == "2026-09-03"
    assert str(vc.parse_day("2026-09-04T00:30:00+05:00", "UTC")) == "2026-09-03"
    moved = vc.parse_day("2026-09-06T23:00:00-12:00", "Asia/Karachi")
    assert (moved - vc.parse_day("2026-09-06", "Asia/Karachi")).days == 1


def test_timestamp_conversion_feeds_the_ordering_check(tmp_path):
    facts = _base(tmp_path)
    _event(facts, "P")["date"] = "2026-09-04T20:00:00Z"
    assert _codes(vc.validate(tmp_path, facts)) == ["ordering_violation"]


def test_published_repository_chronology_is_supported():
    facts = json.loads((REPO / "evidence" / "timeline_facts.json").read_text(encoding="utf-8"))
    findings = vc.validate(REPO, facts)
    assert findings == [], "\n".join(map(str, findings))
