#!/usr/bin/env python3
"""Check that the published research chronology is supported and consistent.

The validator reads a machine-readable fact file (``evidence/timeline_facts.json``)
and the public documents it names, and reports every claim it cannot support.
It checks:

* that the required timeline paragraph appears verbatim where it must;
* that every date is written in an unambiguous ISO form, converting timestamps
  that carry an offset into the fact file's time zone rather than guessing;
* that statuses come from a fixed vocabulary;
* that every historical, active or completed event cites at least one source,
  and that each cited source exists and is readable in the repository;
* that a target is never marked completed without completion evidence, and that
  no public document claims a target is complete while its status says otherwise;
* that dates respect every ordering the preserved records justify;
* that the primary analysis is not dated after a record that already states its
  outcomes were known;
* that the authoritative real-data run is not relabelled as dummy or setup
  output without correction evidence;
* that any additional analysis has its own plan, execution evidence and results
  appropriate to its status, and does not modify the completed primary analysis.

Limits. A cited file that exists and matches its hash shows which file was
inspected, not that its contents are independently true. File modification
times, Git author dates and a passing check are not treated as proof that a
historical event happened. The validator cannot certify authorship, research
ethics, clinical validity or suitability for any purpose. An unsupported claim
fails however plausible it sounds.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ALLOWED_STATUSES = {"historical", "planned", "active", "completed", "blocked"}
NEEDS_SOURCE = {"historical", "active", "completed"}
NON_REAL_LABELS = {"dummy", "synthetic", "setup", "placeholder", "test"}

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(:\d{2}(\.\d+)?)?(Z|[+-]\d{2}:\d{2})$"
)


@dataclass(frozen=True)
class Finding:
    code: str
    subject: str
    message: str

    def __str__(self) -> str:
        return f"{self.code}: {self.subject}: {self.message}"


class DateFormatError(ValueError):
    pass


def _zone(name: str):
    try:
        from zoneinfo import ZoneInfo
        return ZoneInfo(name)
    except Exception:
        if name == "Asia/Karachi":
            return timezone(timedelta(hours=5))
        if name in ("UTC", "Etc/UTC"):
            return timezone.utc
        raise


def parse_day(value: str, tz_name: str) -> date:
    """Return the calendar date of ``value`` in ``tz_name``.

    Accepts ``YYYY-MM-DD`` or an ISO timestamp with an explicit offset. A
    timestamp without an offset, or any other layout, is rejected rather than
    interpreted, because guessing could move an event to a different day.
    """
    if not isinstance(value, str):
        raise DateFormatError(f"expected an ISO date string, got {value!r}")
    if _DATE_RE.match(value):
        return date.fromisoformat(value)
    if _DATETIME_RE.match(value):
        stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return stamp.astimezone(_zone(tz_name)).date()
    raise DateFormatError(
        f"{value!r} is not YYYY-MM-DD or an ISO timestamp with an offset"
    )


def _event_bounds(event: dict, tz_name: str):
    """(earliest, latest) calendar dates for an event, or None if undated."""
    if event.get("date") is not None:
        d = parse_day(event["date"], tz_name)
        return d, d
    if event.get("start") is not None or event.get("end") is not None:
        lo = parse_day(event["start"], tz_name) if event.get("start") else None
        hi = parse_day(event["end"], tz_name) if event.get("end") else None
        return lo or date.min, hi or date.max
    if event.get("target_date") is not None:
        d = parse_day(event["target_date"], tz_name)
        return d, d
    return None


def _readable(root: Path, rel: str) -> bool:
    try:
        path = (root / rel).resolve()
        path.relative_to(root.resolve())
    except (ValueError, OSError):
        return False
    return path.is_file() and path.stat().st_size > 0


def validate(root: Path, facts: dict) -> list[Finding]:
    root = Path(root)
    tz_name = facts.get("timezone", "UTC")
    out: list[Finding] = []
    events = facts.get("events", [])
    by_id: dict[str, dict] = {}
    bounds: dict[str, tuple] = {}

    # Required wording
    required = facts.get("required_wording")
    if required:
        text = required["text"]
        for rel in required.get("files", []):
            if not _readable(root, rel):
                out.append(Finding("missing_source", rel, "file carrying the required wording is missing"))
            elif text not in (root / rel).read_text(encoding="utf-8"):
                out.append(Finding("required_wording_missing", rel, "the required timeline paragraph is not present verbatim"))

    for ev in events:
        eid = ev.get("id", "<no id>")
        if eid in by_id:
            out.append(Finding("duplicate_event_id", eid, "event identifiers must be unique"))
        by_id[eid] = ev
        status = ev.get("status")
        if status not in ALLOWED_STATUSES:
            out.append(Finding("invalid_status", eid, f"status {status!r} is not one of {sorted(ALLOWED_STATUSES)}"))

        try:
            b = _event_bounds(ev, tz_name)
        except DateFormatError as e:
            out.append(Finding("invalid_date_format", eid, str(e)))
            b = False
        if b:
            if b[0] > b[1]:
                out.append(Finding("invalid_date_range", eid, "range starts after it ends"))
            bounds[eid] = b
        elif b is None and ev.get("date_status") != "unestablished":
            out.append(Finding("undated_event", eid, "no date given and not marked unestablished"))

        sources = ev.get("sources", [])
        if status in NEEDS_SOURCE and not sources and ev.get("type") != "target":
            out.append(Finding("unsupported_claim", eid, f"a {status} event cites no source"))
        for rel in sources:
            if not _readable(root, rel):
                out.append(Finding("missing_source", eid, f"cited source {rel!r} is missing or unreadable"))

        if ev.get("type") == "target":
            if status == "historical":
                out.append(Finding("invalid_status", eid, "a target cannot be historical"))
            if status == "completed":
                evidence = ev.get("completion_evidence", [])
                if not evidence or not all(_readable(root, r) for r in evidence):
                    out.append(Finding("target_completed_without_evidence", eid, "a target is marked completed without readable completion evidence"))
            if status != "completed":
                for phrase in ev.get("completion_phrases", []):
                    for rel in facts.get("claim_documents", []):
                        if _readable(root, rel) and phrase.lower() in (root / rel).read_text(encoding="utf-8").lower():
                            out.append(Finding("completion_claim_contradicts_status", eid, f"{rel} says {phrase!r} while the target is {status}"))

        run_label = ev.get("data_kind")
        if ev.get("authoritative_run") and run_label in NON_REAL_LABELS and not ev.get("correction_evidence"):
            out.append(Finding("relabelled_real_run", eid, f"the authoritative real-data run is labelled {run_label!r} without correction evidence"))

    # Ordering justified by the preserved records
    for pair in facts.get("ordering", []):
        a, b = pair
        if a not in by_id or b not in by_id:
            out.append(Finding("unknown_event", f"{a} -> {b}", "ordering refers to an unknown event"))
            continue
        if a in bounds and b in bounds and bounds[a][0] > bounds[b][1]:
            out.append(Finding("ordering_violation", f"{a} -> {b}", f"{a} cannot precede {b} on the stated dates"))

    # The primary analysis cannot postdate a record that says its outcomes were known
    known = [bounds[e["id"]][1] for e in events if e.get("records_primary_outcomes_known") and e.get("id") in bounds]
    for ev in events:
        if ev.get("anchor") == "primary_analysis_completed" and ev.get("id") in bounds and known:
            if bounds[ev["id"]][0] > min(known):
                out.append(Finding("primary_after_outcomes_known", ev["id"], "the primary analysis is dated after a record that already states its outcomes were known"))

    primary_ids = {e["id"] for e in events if e.get("anchor") == "primary_analysis_completed"}
    for an in facts.get("additional_analyses", []):
        aid = an.get("id", "<no id>")
        status = an.get("status")
        if status not in ALLOWED_STATUSES - {"historical"}:
            out.append(Finding("invalid_status", aid, f"status {status!r} is not allowed for an additional analysis"))
        if not an.get("plan") or not _readable(root, an["plan"]):
            out.append(Finding("additional_analysis_without_plan", aid, "no readable dated plan"))
        if status in {"active", "completed"}:
            ev_files = an.get("execution_evidence", [])
            if not ev_files or not all(_readable(root, r) for r in ev_files):
                out.append(Finding("additional_analysis_without_execution_evidence", aid, f"a {status} analysis needs readable execution evidence"))
        if status == "completed":
            res = an.get("results", [])
            if not res or not all(_readable(root, r) for r in res):
                out.append(Finding("additional_analysis_without_results", aid, "a completed analysis needs readable results"))
        if set(an.get("modifies_events", [])) & primary_ids:
            out.append(Finding("additional_analysis_modifies_primary", aid, "an additional analysis may not alter the completed primary analysis"))
        try:
            if an.get("start"):
                parse_day(an["start"], tz_name)
        except DateFormatError as e:
            out.append(Finding("invalid_date_format", aid, str(e)))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".", help="repository root")
    ap.add_argument("--facts", default="evidence/timeline_facts.json")
    a = ap.parse_args(argv)
    root = Path(a.root)
    facts = json.loads((root / a.facts).read_text(encoding="utf-8"))
    findings = validate(root, facts)
    n_events = len(facts.get("events", []))
    n_extra = len(facts.get("additional_analyses", []))
    if findings:
        for f in findings:
            print(f)
        print(f"UNRESOLVED: {len(findings)} finding(s) across {n_events} events and {n_extra} additional analyses")
        return 1
    print(f"SUPPORTED: {n_events} events and {n_extra} additional analyses; no unresolved finding")
    return 0


if __name__ == "__main__":
    sys.exit(main())
