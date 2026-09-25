#!/usr/bin/env python3
"""
Reproduction gates (prereg 18.1).  Gate A compares upstream code against its own
committed outputs; Gate B compares our pipeline against published cohort numbers.
Neither gate may be relaxed to make a number match.
"""
import json, subprocess, sys
from pathlib import Path

UPSTREAM = {
    "WearableDetection": ("https://github.com/mwgrassgreen/WearableDetection", "38955bc0"),
    "Alarm": ("https://github.com/mwgrassgreen/Alarm", "1770dd0d"),
    "AnomalyDetect": ("https://github.com/gireeshkbogu/AnomalyDetect", "1484183d"),
    "wearable-infection": ("https://github.com/StanfordBioinformatics/wearable-infection",
                           "99b3bd79"),
}

GATE_B = {
    "mishra_analysed_cases": dict(published=32, tol=0),
    "mishra_detected": dict(published=26, tol=2),
    "mishra_median_lead_days_vs_onset": dict(published=4, tol=1),
    "mishra_detected_at_or_before_onset_of_25": dict(published=22, tol=2),
    "alavi_confirmed_positives": dict(published=84, tol=0),
    "alavi_sensitivity_per_person_pct": dict(published=80.0, tol=5.0,
                                             denominator="67/84 participants"),
    "alavi_specificity_per_alert_day_pct": dict(published=87.7, tol=2.0,
                                                denominator="87124/(87124+12186) alert-days"),
}


def clone_all(dest="src/upstream"):
    Path(dest).mkdir(parents=True, exist_ok=True)
    rec = {}
    for name, (url, want) in UPSTREAM.items():
        p = Path(dest) / name
        if not p.exists():
            subprocess.run(["git", "clone", "--quiet", url, str(p)], check=True)
        subprocess.run(["git", "-C", str(p), "checkout", "--quiet", want], check=True)
        got = subprocess.run(["git", "-C", str(p), "rev-parse", "HEAD"],
                             capture_output=True, text=True, check=True).stdout.strip()
        rec[name] = dict(url=url, requested=want, head=got)
    json.dump(rec, open("docs/upstream_commits.json", "w"), indent=2)
    return rec


def gate_b_report(observed: dict) -> dict:
    out = {}
    for k, spec in GATE_B.items():
        if k not in observed:
            out[k] = dict(status="NOT_RUN", **spec); continue
        ok = abs(observed[k] - spec["published"]) <= spec["tol"]
        out[k] = dict(status="PASS" if ok else "FAIL", observed=observed[k], **spec)
    out["_policy"] = ("A failing gate is reported as a finding. Upstream code is NOT "
                      "modified to close it. Schedule comparisons are then anchored to "
                      "our own S1 reference arm, which is internally valid regardless. "
                      "The two Alavi figures are reported with their denominators named "
                      "and never as a matched sensitivity/specificity pair.")
    return out


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clone":
        print(json.dumps(clone_all(), indent=2))
    else:
        print(json.dumps(gate_b_report({}), indent=2))
