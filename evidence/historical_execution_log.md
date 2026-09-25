# Historical execution log: reviewed excerpts

> This document contains reviewed excerpts from a preserved execution record. Personal identifiers, private paths, and ineligible individual-level material have been removed. Omissions are described where relevant. Historical reported outputs are distinguished from newly executed verification.

*The excerpts below are taken from the terminal record of the research, in the order in which they occur there. The record shows the commands I ran and the output they reported between the first data download and the final results commit. Everything inside the code blocks is historical output. The headings and the one-line notes are new writing, added for this repository. The [execution log guide](EXECUTION_LOG_GUIDE.md) explains the conventions, what the record can and cannot establish, and what has been left out.*

**Conventions inside code blocks**

- `$` replaces the account-and-host shell prompt; `(.venv) $` marks commands run with the project's virtual environment active.
- `<PROJECT_ROOT>` replaces the project folder's absolute path, `<DOWNLOADS>` the download folder's path, and `<user>` the account name in file listings.
- `<participant>` replaces a dataset participant identifier.
- `[omitted: …]` marks a gap and says what was left out. Nothing else was changed, apart from the removal of trailing spaces at line ends.

## 1. Data acquisition and archive integrity

### 1.1 First acquisition attempt

The acquisition step of the project runner downloaded the Phase 1 archive in full; the Phase 2 download was stopped at 66%.

```text
Last login: Mon Aug 31 10:45:50 on ttys000
[omitted: shell setup and project-file placement]
$ chmod +x run_phase1.sh
./run_phase1.sh --preflight
== 1. acquire ==
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100  360M  100  360M    0     0  17.9M      0  0:00:20  0:00:20 --:--:-- 18.4M
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
 66 5281M   66 3513M    0     0  17.2M      0  0:05:06  0:03:23  0:01:43 20.3M^C
```

### 1.2 Archive tests and the repeated Phase 2 download

The incomplete Phase 2 file failed the archive test and was downloaded again from the dataset's public storage location.

```text
$ cd <PROJECT_ROOT>/data_raw
unzip -t COVID-19-Wearables.zip
unzip -t COVID-19-Phase2-Wearables.zip
[omitted: 281 archive-member lines naming participant files]
No errors detected in compressed data of COVID-19-Wearables.zip.
Archive:  COVID-19-Phase2-Wearables.zip
  End-of-central-directory signature not found.  Either this file is not
  a zipfile, or it constitutes one disk of a multi-part archive.  In the
  latter case the central directory and zipfile comment will be found on
  the last disk(s) of this archive.
unzip:  cannot find zipfile directory in one of COVID-19-Phase2-Wearables.zip or
        COVID-19-Phase2-Wearables.zip.zip, and cannot find COVID-19-Phase2-Wearables.zip.ZIP, period.
$ shasum -a 256 COVID-19-Wearables.zip
shasum -a 256 COVID-19-Phase2-Wearables.zip
52ca976e6c08daa0cf34b6b82f4fc69b8894c1eef66e598efa40197df4e380f4  COVID-19-Wearables.zip
0eb6a4c5514cbe1e393008b29b6768ac4b3857ace8b13f848b7a4bbf264795e8  COVID-19-Phase2-Wearables.zip
$ cd <PROJECT_ROOT>/data_raw
rm COVID-19-Phase2-Wearables.zip
curl -fL --retry 5 --retry-delay 5 \
-o COVID-19-Phase2-Wearables.zip \
"https://storage.googleapis.com/gbsc-gcp-project-ipop_public/COVID-19-Phase2/COVID-19-Phase2-Wearables.zip"
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100 5281M  100 5281M    0     0  19.1M      0  0:04:35  0:04:35 --:--:-- 18.8M
```

### 1.3 Test and hashes of the archives used

The repeated download passed the archive test. These are the two archives used for every later step.

```text
$ cd <PROJECT_ROOT>/data_raw
unzip -t COVID-19-Phase2-Wearables.zip
Archive:  COVID-19-Phase2-Wearables.zip
[omitted: 8,495 archive-member lines naming participant folders and files]
No errors detected in compressed data of COVID-19-Phase2-Wearables.zip.
$ ls -lh COVID-19-Wearables.zip COVID-19-Phase2-Wearables.zip
shasum -a 256 COVID-19-Wearables.zip
shasum -a 256 COVID-19-Phase2-Wearables.zip
-rw-r--r--  1 <user>  staff   5.2G  1 Sep 10:34 COVID-19-Phase2-Wearables.zip
-rw-r--r--@ 1 <user>  staff   361M  1 Sep 10:23 COVID-19-Wearables.zip
52ca976e6c08daa0cf34b6b82f4fc69b8894c1eef66e598efa40197df4e380f4  COVID-19-Wearables.zip
c90b13146d3996b4d2159c4af31115b9ba2cb3c3fc2e15565b34c016ced9c994  COVID-19-Phase2-Wearables.zip
```

## 2. Environment

### 2.1 Missing dependencies, then a working environment

The runner's preflight first failed because the scientific packages were not installed; the project had lock files but no plain requirements file.

```text
[omitted: placement of an updated copy of the project code]
$ cd <PROJECT_ROOT>
./run_phase1.sh --preflight
== preflight ==
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'numpy'
FATAL: python dependencies missing
$ cd <PROJECT_ROOT>
python3 -m venv .venv
source .venv/bin/activate
[omitted: package-manager upgrade output]
(.venv) $ if [ -f environment/requirements.txt ]; then
    pip install -r environment/requirements.txt
elif [ -f requirements.txt ]; then
    pip install -r requirements.txt
else
    echo "NO REQUIREMENTS FILE FOUND"
    find environment -maxdepth 2 -type f -print
fi
NO REQUIREMENTS FILE FOUND
environment/Dockerfile.upstream-py36
environment/provenance.txt
environment/upstream-venv-requirements.lock
environment/legacy-venv-requirements.lock
environment/Dockerfile.upstream-R
environment/requirements.lock
(.venv) $ ./run_phase1.sh --preflight
== preflight ==
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
ModuleNotFoundError: No module named 'numpy'
FATAL: python dependencies missing
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
pip install numpy pandas scipy pytest pyarrow
[omitted: package download and installation output]
(.venv) $ python -c "import numpy,pandas,scipy,pytest,pyarrow; print('OK')"
OK
(.venv) $ ./run_phase1.sh --preflight
== preflight ==
  python deps ok: 2.5.2 3.0.5
  scripts present
  COVID-19-Wearables.zip already present ( 378380920 bytes) — will be used as supplied
  COVID-19-Phase2-Wearables.zip already present ( 5537624129 bytes) — will be used as supplied
  WARNING: results/onset_labels.csv absent — required first; the device
      gate is scoped to the candidates it names
  NOTE: no results/device_map_external.csv — Phase 1 rows will be UNKNOWN
  preflight OK
preflight only; nothing computed.
```

## 3. Onset labels and device provenance

### 3.1 Supplementary tables and onset labels

Onset dates are taken from the dataset papers' supplementary tables, never inferred from physiology.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
mkdir -p metadata
pip install openpyxl
curl -fL -o metadata/phase1_supplementary_data.xlsx \
"https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41551-020-00640-6/MediaObjects/41551_2020_640_MOESM3_ESM.xlsx"
curl -fL -o metadata/phase2_covid_metadata.xlsx \
"https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41591-021-01593-2/MediaObjects/41591_2021_1593_MOESM3_ESM.xlsx"
ls -lh metadata/
[omitted: installation, transfer and file-listing output]
(.venv) $ wc -l results/onset_labels.csv
head -5 results/onset_labels.csv
     117 results/onset_labels.csv
phase,participant_id,device,symptomatic,onset_date,diagnosis_date,source,source_locator,retrieved_utc
[omitted: four example rows of participant onset labels]
(.venv) $ ./run_phase1.sh --preflight
== preflight ==
  python deps ok: 2.5.2 3.0.5
  scripts present
  COVID-19-Wearables.zip already present ( 378380920 bytes) — will be used as supplied
  COVID-19-Phase2-Wearables.zip already present ( 5537624129 bytes) — will be used as supplied
  onset_labels.csv present
  NOTE: no results/device_map_external.csv — Phase 1 rows will be UNKNOWN
  preflight OK
preflight only; nothing computed.
```

### 3.2 Phase label correction

The label file used numeric phase codes that the pipeline did not expect; a copy was kept before the correction.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
cp results/onset_labels.csv results/onset_labels_before_phase_fix.csv
python - <<'PY'
import pandas as pd
p = "results/onset_labels.csv"
df = pd.read_csv(p)
df["phase"] = df["phase"].replace({
    1: "phase1",
    2: "phase2",
    "1": "phase1",
    "2": "phase2"
})
assert set(df["phase"]) == {"phase1", "phase2"}
assert len(df) == 116
df.to_csv(p, index=False)
print(df.groupby("phase").size())
print("\nSaved corrected:", p)
PY
phase
phase1    32
phase2    84
dtype: int64
Saved corrected: results/onset_labels.csv
```

## 4. Inventory

### 4.1 Timestamp-unit defect and its fix

The Phase 1 inventory failed an internal range check. The cause was a timestamp-unit conversion; a copy of the script was kept before the fix, and the test suite was re-run.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python src/zip_inventory.py \
  --zip data_raw/COVID-19-Wearables.zip \
  --phase phase1
phase1: opening data_raw/COVID-19-Wearables.zip
Traceback (most recent call last):
  File "<PROJECT_ROOT>/src/zip_inventory.py", line 391, in <module>
    main()
    ~~~~^^
  File "<PROJECT_ROOT>/src/zip_inventory.py", line 334, in main
    cov = coverage_from_minutes(all_minutes, all_raw)
  File "<PROJECT_ROOT>/src/zip_inventory.py", line 203, in coverage_from_minutes
    assert out.day_observed_minutes.between(0, 1020).all()
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
AssertionError
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
cp src/zip_inventory.py src/zip_inventory_before_datetime_fix.py
python - <<'PY'
from pathlib import Path
p = Path("src/zip_inventory.py")
s = p.read_text()
old1 = '''            mins = ts.dt.floor("min").astype("int64").unique()
            minutes.update(int(x) for x in mins)'''
new1 = '''            mins = (
                ts.dt.floor("min")
                .to_numpy(dtype="datetime64[ns]")
                .astype("int64")
            )
            minutes.update(int(x) for x in np.unique(mins))'''
old2 = '''            secs = np.sort(
                (ts.astype("int64").to_numpy() // 1_000_000_000)
            )'''
new2 = '''            secs = np.sort(
                ts.to_numpy(dtype="datetime64[ns]").astype("int64")
                // 1_000_000_000
            )'''
old3 = '''    dt = pd.Series(pd.to_datetime(arr))'''
new3 = '''    dt = pd.Series(pd.to_datetime(arr, unit="ns"))'''
for old, new in [(old1,new1),(old2,new2),(old3,new3)]:
    if old not in s:
        raise SystemExit("EXPECTED CODE NOT FOUND — STOPPING WITHOUT MODIFYING FILE")
    s = s.replace(old,new)
p.write_text(s)
print("Datetime-unit patch applied successfully.")
PY
Datetime-unit patch applied successfully.
(.venv) $ python -m pytest tests/ -q
...................................................................................................................................                                                                     [100%]
131 passed in 31.73s
(.venv) $ python src/zip_inventory.py \
  --zip data_raw/COVID-19-Wearables.zip \
  --phase phase1
phase1: opening data_raw/COVID-19-Wearables.zip
  50/118 HR participants
  100/118 HR participants
  118/118 HR participants
=== SUMMARY ===
phase: phase1
CSV files: 280
unmatched: 0
HR participants: 118
participant-days: 10355
devices:
device
UNKNOWN    118
duplicate participant-days: 0
DONE: phase1
```

### 4.2 Malformed Phase 2 file

The Phase 2 inventory stopped on one heart-rate file whose content was an error message rather than data.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python src/zip_inventory.py \
  --zip data_raw/COVID-19-Phase2-Wearables.zip \
  --phase phase2
phase2: opening data_raw/COVID-19-Phase2-Wearables.zip
[omitted: progress lines]
<PROJECT_ROOT>/src/phase1_inventory.py:72: UserWarning: Could not infer format, so each element will be parsed individually, falling back to `dateutil`. To ensure parsing is consistent and as-expected, please specify a format.
  return pd.to_datetime(df[lower[cand]], errors="coerce")
[omitted: progress lines]
Traceback (most recent call last):
  File "<PROJECT_ROOT>/src/zip_inventory.py", line 396, in <module>
    main()
    ~~~~^^
  File "<PROJECT_ROOT>/src/zip_inventory.py", line 317, in main
    mins, raw, native = read_hr_member(z, info)
                        ~~~~~~~~~~~~~~^^^^^^^^^
  File "<PROJECT_ROOT>/src/zip_inventory.py", line 112, in read_hr_member
    ts = parse_timestamps(chunk).dropna()
         ~~~~~~~~~~~~~~~~^^^^^^^
  File "<PROJECT_ROOT>/src/phase1_inventory.py", line 73, in parse_timestamps
    raise RuntimeError(f"no timestamp column found; columns were {list(df.columns)}")
RuntimeError: no timestamp column found; columns were ['Error in query string: Error processing job']
```

### 4.3 Quarantine and device provenance

After the quarantine change (the pre-change script is kept), the malformed file was recorded and skipped rather than guessed. Every infection-positive candidate then had a device assignment with stated provenance.

```text
[omitted: patch script; the change is visible by comparing evidence/historical_code/zip_inventory_before_quarantine_fix.py with src/zip_inventory.py]
(.venv) $ python src/zip_inventory.py \
  --zip data_raw/COVID-19-Phase2-Wearables.zip \
  --phase phase2
phase2: opening data_raw/COVID-19-Phase2-Wearables.zip
[omitted: progress lines]
=== SUMMARY ===
phase: phase2
CSV files: 4246
unmatched: 0
HR participants: 2122
participant-days: 252067
quarantined HR files: 1
devices:
device
Fitbit     1027
UNKNOWN    1095
duplicate participant-days: 0
DONE: phase2
(.venv) $ cat results/quarantined_hr_files_phase2.json
[
  {
    "phase": "phase2",
    "participant_id": "<participant>",
    "source_file": "COVID-19-Phase2-Wearables/<participant>/Orig_NonFitbit_HR.csv",
    "reason": "no timestamp column found; columns were ['Error in query string: Error processing job']"
  }
]%                                                                                                                                                                                                             (.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python src/build_device_map.py \
  --inventory results/inventory_phase1.parquet results/inventory_phase2.parquet \
  --external results/device_map_external.csv
python src/check_device_coverage.py \
  --device-map results/device_map.csv \
  --onsets results/onset_labels.csv
phase   device
phase1  Fitbit          32
        UNKNOWN         86
phase2  AppleWatch      35
        Fitbit        1027
        UNKNOWN       1060
1146 participants have no defensible device assignment. They are EXCLUDED from the cohort, not guessed. Resolve them by supplying --external with supplementary-table or correspondence rows.
{
  "total_participants_in_map": 2240,
  "total_unknown_or_conflict_all_participants": 1146,
  "note_on_total": "Reported for transparency only. Unresolved devices among participants who are NOT infection candidates do not block the pipeline.",
  "n_candidates": 116,
  "candidates_resolved": 116,
  "candidates_unresolved": 0,
  "candidates_absent_from_device_map": [],
  "n_candidates_absent_from_device_map": 0,
  "unresolved_candidate_ids": [],
  "blocking": false
}
All candidate infection-positive participants have a device with provenance.
(.venv) $ python - <<'PY'
import pandas as pd
dm = pd.read_csv("results/device_map.csv")
on = pd.read_csv("results/onset_labels.csv")
x = on.merge(
    dm,
    on=["phase","participant_id"],
    how="left",
    suffixes=("_label","_map")
)
print("\n=== CANDIDATE DEVICE AUDIT ===")
print(x.groupby(["phase","device_map","provenance"]).size())
bad = x[
    x.device_map.isna() |
    x.device_map.isin(["UNKNOWN","CONFLICT"])
]
print("\nUnresolved candidates:", len(bad))
if len(bad):
    print(bad[["phase","participant_id","device_map","provenance"]])
PY
=== CANDIDATE DEVICE AUDIT ===
phase   device_map  provenance
phase1  Fitbit      paper_statement_scope    32
phase2  AppleWatch  supplementary_table      35
        Fitbit      filename_token           49
dtype: int64
Unresolved candidates: 0
```

## 5. Cohort

### 5.1 Cohort construction

Counts only; no per-participant rows.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python src/build_cohort.py \
  --inventory results/inventory_phase1.parquet results/inventory_phase2.parquet \
  --onsets results/onset_labels.csv \
  --device-map results/device_map.csv
{
  "per_phase": {
    "phase1": {
      "infection_positive": 32,
      "device_Fitbit_with_provenance": 32,
      "device_unknown_or_conflict": 0,
      "of_which_symptomatic": 30,
      "with_onset_date": 30,
      "sufficient_baseline": 18,
      "pre_calibration_eligible": 18
    },
    "phase2": {
      "infection_positive": 84,
      "device_Fitbit_with_provenance": 49,
      "device_unknown_or_conflict": 0,
      "of_which_symptomatic": 37,
      "with_onset_date": 37,
      "sufficient_baseline": 31,
      "pre_calibration_eligible": 31
    }
  },
  "pre_calibration_eligible_total": 49,
  "calibration_days_distribution": {
    "median": 46.0,
    "iqr": [
      34.0,
      112.0
    ],
    "minimum": 0.0,
    "maximum": 407.0,
    "shares": {
      "28": 0.7755102040816326,
      "42": 0.6326530612244898,
      "61": 0.3469387755102041,
      "91": 0.30612244897959184
    },
    "floor": 0.8
  },
  "chosen_C_min": 28,
  "C_min_selection_rule": "availability-only rule; frozen before any outcome inspection",
  "excluded_for_C_p_below_C_min": 11,
  "FINAL_ELIGIBLE_N": 38,
  "budget_used_for_resolution_reporting": 2.0,
  "one_alert_resolution_at_chosen_C_min": 1.087
}
```

### 5.2 Final cohort by phase

The eleven participants excluded for too few calibration days are listed in the record by identifier; those lines are omitted.

```text
(.venv) $ python - <<'PY'
import json
from collections import Counter
c = json.load(open("results/cohort.json"))
print("Pre-calibration:", Counter(x[0] for x in c["pre_calibration"]))
print("Final:", Counter(x[0] for x in c["final"]))
print("Final N:", len(c["final"]))
cal = c["calibration_days"]
excluded = [
    (ph, pid, cal[f"{ph}:{pid}"])
    for ph, pid in c["pre_calibration"]
    if [ph, pid] not in c["final"]
]
print("\nExcluded for C_p below chosen threshold:")
for x in sorted(excluded):
    print(x)
PY
Pre-calibration: Counter({'phase2': 31, 'phase1': 18})
Final: Counter({'phase2': 28, 'phase1': 10})
Final N: 38
Excluded for C_p below chosen threshold:
[omitted: 11 per-participant exclusion lines]
```

### 5.3 Coverage label clarification, coverage diagnostic and overlap check

A copy of the coverage script was kept before a label change; amendment A3.8 records the reason. The overlap check returned UNDETERMINABLE, and A3.9 records the consequences.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
cp src/coverage_diagnostic.py src/coverage_diagnostic_before_label_fix.py
python - <<'PY'
from pathlib import Path
p = Path("src/coverage_diagnostic.py")
s = p.read_text()
s = s.replace(
    '"A_all_fitbit"',
    '"A_provenance_resolved_fitbit"'
)
p.write_text(s)
doc = Path("docs/prereg-v1.2-amendment-A3.md")
with doc.open("a") as f:
    f.write("""
## A3.8 — Coverage population A device-provenance clarification
The published Phase-1 supplementary workbook does not provide a per-participant
device mapping for the non-COVID archive participants. They therefore remain
UNKNOWN rather than being blanket-assigned Fitbit.
Coverage population A is consequently labelled
`A_provenance_resolved_fitbit`, not `A_all_fitbit`. It contains only
participants whose Fitbit assignment has explicit provenance.
Populations B (pre-calibration eligible) and C (final primary cohort) are
unchanged because every infection-positive candidate has a resolved device
assignment. This clarification does not alter cohort membership, C_min,
confirmatory hypotheses, or any outcome definition.
""")
print("Coverage label + provenance clarification applied.")
PY
Coverage label + provenance clarification applied.
(.venv) $ python src/coverage_diagnostic.py \
  --inventory results/inventory_phase1.parquet results/inventory_phase2.parquet \
  --device-map results/device_map.csv \
  --cohort results/cohort.json
[
  {
    "population": "A_provenance_resolved_fitbit",
    "n_participants": 1059,
    "mean_night_coverage": 0.851169338985839,
    "mean_day_coverage": 0.8601376630361522,
    "mean_paired_difference": -0.008968324050313116,
    "ci95": [
      -0.019755672789134034,
      0.0011174630322565494
    ],
    "bootstrap_unit": "participant",
    "interpretation": "positive = night better covered than day"
  },
  {
    "population": "B_pre_calibration_eligible",
    "n_participants": 49,
    "mean_night_coverage": 0.9445340498833672,
    "mean_day_coverage": 0.9240444411488374,
    "mean_paired_difference": 0.020489608734529593,
    "ci95": [
      0.008513332446305266,
      0.032103742128401724
    ],
    "bootstrap_unit": "participant",
    "interpretation": "positive = night better covered than day"
  },
  {
    "population": "C_final_primary_cohort",
    "n_participants": 38,
    "mean_night_coverage": 0.9371865762999249,
    "mean_day_coverage": 0.9215666767925748,
    "mean_paired_difference": 0.015619899507350198,
    "ci95": [
      0.0006957065595539577,
      0.029270616004963494
    ],
    "bootstrap_unit": "participant",
    "interpretation": "positive = night better covered than day"
  }
]
(.venv) $ python src/check_overlap.py \
  results/inventory_phase1.parquet \
  results/inventory_phase2.parquet
{
  "shared_identifiers": [],
  "n_shared": 0,
  "date_plausibility": {
    "phase1": {
      "phase": "phase1",
      "plausible": false,
      "frac_in_window": 0.0,
      "observed_range": [
        "2022-01-18",
        "2030-09-03"
      ],
      "published_window": [
        "2020-01-01",
        "2021-03-31"
      ]
    },
    "phase2": {
      "phase": "phase2",
      "plausible": false,
      "frac_in_window": 7.537678474373877e-05,
      "observed_range": [
        "2021-01-31",
        "2029-12-31"
      ],
      "published_window": [
        "2020-11-27",
        "2021-07-20"
      ]
    }
  },
  "hr_series_check_performed": false,
  "supplementary_coverage_check_performed": false,
  "flagged_pairs": [],
  "supplementary_flagged_pairs": [],
  "n_pairs_compared": 0,
  "verdict": "UNDETERMINABLE",
  "basis": "calendar dates in at least one archive fall outside the published study window, so cross-release date alignment is invalid. No series comparison of any kind was performed. See date_plausibility.",
  "note": "The Phase-2-only sensitivity analysis runs regardless of this verdict. The verdict changes what Methods says, not what is computed."
}
(.venv) $ cd <PROJECT_ROOT>
cat >> docs/prereg-v1.2-amendment-A3.md <<'EOF'
## A3.9 — Source-coverage diagnostic decision, before outcome analysis
The mandatory pre-masking coverage diagnostic was completed before any
schedule-performance outcome was computed.
In the final primary cohort (N=38), mean observed-minute coverage was
0.9372 in the nocturnal window and 0.9216 in the daytime window.
The participant-bootstrap paired difference (night minus day) was
+0.0156, with 95% CI [0.0007, 0.0293].
Because the earlier wording "differ materially" did not define a numerical
threshold, no post-hoc magnitude threshold is introduced. Conservatively,
the prespecified additional realised-sample-count-conditioned analysis is
therefore mandatory for M1 (S3r versus S6), regardless of whether it changes
the conclusion. It supplements rather than replaces the primary paired M1
analysis.
The overlap investigation returned UNDETERMINABLE because archive calendar
dates are inconsistent with the published study windows. No cross-release
physiological-series identity test was performed. The prespecified
Phase-2-only sensitivity analysis therefore remains mandatory.
EOF
```

## 6. Power calculation

### 6.1 Frozen power calculation at the audited N

The audited cohort size was written into the script (a copy was kept before the change), its tests were run, and the frozen calculation was produced.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
cp src/power_sim.py src/power_sim_before_n38.py
python - <<'PY'
from pathlib import Path
p = Path("src/power_sim.py")
s = p.read_text()
old = "AUDITED_N = None"
new = "AUDITED_N = 38"
if old not in s:
    raise SystemExit("AUDITED_N placeholder not found — no change made")
p.write_text(s.replace(old, new, 1))
print("AUDITED_N set to 38.")
PY
python -m pytest tests/test_power_sim.py -q
AUDITED_N set to 38.
.............                                                                                                                                                                                           [100%]
13 passed in 0.74s
(.venv) $ python src/power_sim.py \
  --audited \
  --frozen \
  --reps 4000 \
  --sweep-p-b 0.40,0.50,0.60 \
  --surface \
  --out results/power_sim_frozen_n38.json
AUDITED RUN
   n   dependence  rho_d  rho_L  MDE dp  MDE dd   power   disc  n_both  CIhw_th  CIhw_d*
----------------------------------------------------------------------------------------
  38  independent   0.00   0.00    0.25     2.5   0.812   29.1    10.0    0.119     1.53
  38          low   0.25   0.25    0.25     2.5   0.904   27.5    11.3    0.111     1.27
  38     moderate   0.50   0.50    0.20     2.0   0.884   24.3    12.1    0.106     1.01
  38         high   0.75   0.75    0.15     1.5   0.891   20.4    13.2    0.097     0.71
  38  independent   0.00   0.00    0.25     2.5   0.889   31.8    14.2    0.119     1.32
  38          low   0.25   0.25    0.20     2.0   0.827   29.2    14.7    0.118     1.12
  38     moderate   0.50   0.50    0.20     2.0   0.949   27.4    16.1    0.108     0.90
  38         high   0.75   0.75    0.15     1.5   0.949   23.3    17.0    0.100     0.64
  38  independent   0.00   0.00    0.20     2.0   0.817   32.9    18.3    0.126     1.16
  38          low   0.25   0.25    0.20     2.0   0.922   31.5    19.3    0.118     0.99
  38     moderate   0.50   0.50    0.15     1.5   0.832   28.2    19.6    0.116     0.81
  38         high   0.75   0.75    0.15     1.5   0.983   26.0    21.1    0.100     0.58
CIhw_d* = CI half-width for the paired warning difference, detected-under-both only.
wrote results/power_sim_frozen_n38.json  sha256(script) = 3e1d5ecd8bef4915
```

## 7. Upstream reproduction: Gate A

### 7.1 Upstream repositories at their pinned commits

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
mkdir -p src/upstream
cd src/upstream
set -e
git clone https://github.com/mwgrassgreen/WearableDetection
git -C WearableDetection checkout 38955bc0
git clone https://github.com/mwgrassgreen/Alarm
git -C Alarm checkout 1770dd0d
git clone https://github.com/gireeshkbogu/AnomalyDetect
git -C AnomalyDetect checkout 1484183d
git clone https://github.com/StanfordBioinformatics/wearable-infection
git -C wearable-infection checkout 99b3bd79
echo
echo "=== PINNED COMMITS ==="
for d in WearableDetection Alarm AnomalyDetect wearable-infection; do
    echo "$d $(git -C "$d" rev-parse HEAD)"
done | tee <PROJECT_ROOT>/docs/upstream_commits.txt
echo
echo "=== DISK USAGE ==="
du -sh WearableDetection Alarm AnomalyDetect wearable-infection
[omitted: clone and checkout output]
=== PINNED COMMITS ===
WearableDetection 38955bc09e14b446452c01e87e6f525e99e8be6e
Alarm 1770dd0d2f620940e93ec82f8a5ba48b9fde9658
AnomalyDetect 1484183d203ffd1ffce6974a0dbdc66a7c9e0bf3
wearable-infection 99b3bd7937e72d42c2670c7a259d9f9f8728dc06
=== DISK USAGE ===
 34M	WearableDetection
184K	Alarm
196M	AnomalyDetect
 78M	wearable-infection
```

### 7.2 R environment

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
echo "=== R ENVIRONMENT ==="
command -v Rscript || true
Rscript --version 2>&1 || true
Rscript -e 'cat("xts installed:", requireNamespace("xts", quietly=TRUE), "\n")' 2>&1 || true
[omitted: the remaining inspection commands and their output (requirements files and reference-output headers)]
=== R ENVIRONMENT ===
/usr/local/bin/Rscript
Rscript (R) version 4.5.1 (2025-06-13)
xts installed: TRUE
```

### 7.3 Gate A feasibility clarification

Recorded as A3.10 before any schedule-performance analysis.

```text
(.venv) $ cat >> docs/prereg-v1.2-amendment-A3.md <<'EOF'
## A3.10 — Reproduction Gate A feasibility clarification
Inspection of the four pinned upstream repositories was completed before any
schedule-performance analysis.
The original Gate A wording required every upstream repository to reproduce
a committed reference output exactly. Repository inspection showed that this
criterion is not technically evaluable for all four repositories:
- WearableDetection supplies sample participant data and committed
  machine-readable RHR-Diff and CuSum outputs.
- AnomalyDetect supplies sample participant data and committed
  machine-readable HROSAD/RHRAD outputs.
- Alarm supplies the algorithm implementation but no repository-shipped
  sample input/reference-output pair.
- wearable-infection supplies NightSignal sample inputs and an illustrative
  image/README example, but no complete committed machine-readable
  NS-signals.json reference suitable for exact comparison.
Gate A is therefore split prospectively into:
A1: exact reproduction where a repository-shipped sample/reference pair exists;
A2: execution smoke test on repository-shipped sample data where no complete
reference pair exists.
No upstream source file may be edited to obtain a pass. Any environment shim
must be recorded and must leave the upstream file checksum unchanged.
This clarification changes only the feasibility criterion for reproduction;
it does not alter cohort selection, schedules, endpoints, hypotheses or
statistical analysis.
EOF
```

### 7.4 HROS-AD attempts in the current environment

Three attempts failed. In each the upstream script's hash was unchanged before and after the run.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
rm -rf results/gate_a/hrosad_ahyi
mkdir -p results/gate_a/hrosad_ahyi
REF="src/upstream/AnomalyDetect/results/hrosad_offline/HROSAD_anomalies_<participant>.csv"
OUT="results/gate_a/hrosad_ahyi/HROSAD_anomalies_<participant>.csv"
FIG="results/gate_a/hrosad_ahyi/HROSAD_<participant>.pdf"
SCRIPT="src/upstream/AnomalyDetect/scripts/hrosad_offline.py"
# Upstream writer appends rows without writing the header.
head -n 1 "$REF" > "$OUT"
echo "=== SCRIPT HASH BEFORE ==="
shasum -a 256 "$SCRIPT"
echo "=== RUN ==="
python src/gate_a_shim.py "$SCRIPT" \
  --heart_rate src/upstream/AnomalyDetect/data/<participant>_hr.csv \
  --steps src/upstream/AnomalyDetect/data/<participant>_steps.csv \
  --myphd_id myphd_id \
  --figure "$FIG" \
  --anomalies "$OUT" \
  --outliers_fraction 0.1 \
  --random_seed 10 \
  > results/gate_a/hrosad_ahyi/stdout.log \
  2> results/gate_a/hrosad_ahyi/stderr.log
STATUS=$?
[omitted: the same command block, entered again in a new terminal window after the first entry stopped at a comment line]
=== SCRIPT HASH BEFORE ===
1496e8e911dc2cf37d9f683eee087d908dc59d1eefdeea17bbed6df7d708d5aa  src/upstream/AnomalyDetect/scripts/hrosad_offline.py
=== RUN ===
=== EXIT STATUS ===
1
=== STDERR ===
[gate_a_shim] upstream hrosad_offline.py sha256=1496e8e911dc2cf37d9f683eee087d908dc59d1eefdeea17bbed6df7d708d5aa
[gate_a_shim] upstream hrosad_offline.py sha256=1496e8e911dc2cf37d9f683eee087d908dc59d1eefdeea17bbed6df7d708d5aa (UNCHANGED)
Traceback (most recent call last):
  File "<PROJECT_ROOT>/src/gate_a_shim.py", line 38, in <module>
    runpy.run_path(str(target), run_name="__main__")
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen runpy>", line 287, in run_path
  File "<frozen runpy>", line 98, in _run_module_code
  File "<frozen runpy>", line 88, in _run_code
  File "src/upstream/AnomalyDetect/scripts/hrosad_offline.py", line 33, in <module>
    import seaborn as sns
ModuleNotFoundError: No module named 'seaborn'
=== SCRIPT HASH AFTER ===
1496e8e911dc2cf37d9f683eee087d908dc59d1eefdeea17bbed6df7d708d5aa  src/upstream/AnomalyDetect/scripts/hrosad_offline.py
=== REFERENCE / GENERATED HASHES ===
48458571e2d1e80bb3b2f8a091ed572e6582f255db29a1db0acadb097342287f  src/upstream/AnomalyDetect/results/hrosad_offline/HROSAD_anomalies_<participant>.csv
5093e38b7507716988c61c844e0abf8afb81e8c128fae823d5cd0fb1806cace6  results/gate_a/hrosad_ahyi/HROSAD_anomalies_<participant>.csv
=== BYTE COMPARISON ===
GATE A1 HROSAD <participant>: NOT BYTE-IDENTICAL
[omitted: diff of reference rows (hourly anomaly rows of the upstream sample participant)]
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python -m pip install seaborn scikit-learn statsmodels
[omitted: installation output, and the second attempt's command block, which repeats the first]
=== EXIT STATUS ===
1
=== STDERR ===
[gate_a_shim] upstream hrosad_offline.py sha256=1496e8e911dc2cf37d9f683eee087d908dc59d1eefdeea17bbed6df7d708d5aa
[gate_a_shim] upstream hrosad_offline.py sha256=1496e8e911dc2cf37d9f683eee087d908dc59d1eefdeea17bbed6df7d708d5aa (UNCHANGED)
Traceback (most recent call last):
  File "<PROJECT_ROOT>/.venv/lib/python3.14/site-packages/pandas/core/window/rolling.py", line 353, in _prep_values
    values = values.to_numpy(np.float64, na_value=np.nan)
  File "<PROJECT_ROOT>/.venv/lib/python3.14/site-packages/pandas/core/arrays/arrow/array.py", line 1746, in to_numpy
    result = result.astype(dtype, copy=False)
ValueError: could not convert string to float: '<participant>'
[omitted: remaining traceback lines]
pandas.errors.DataError: Cannot aggregate non-numeric type: str
[omitted: creation of the compatibility wrapper src/gate_a_anomalydetect_compat.py and the third attempt's command block; the wrapper is published]
=== EXIT STATUS ===
1
=== STDERR ===
[gate_a_compat] upstream hrosad_offline.py sha256=1496e8e911dc2cf37d9f683eee087d908dc59d1eefdeea17bbed6df7d708d5aa
[gate_a_compat] upstream hrosad_offline.py sha256=1496e8e911dc2cf37d9f683eee087d908dc59d1eefdeea17bbed6df7d708d5aa (UNCHANGED)
Traceback (most recent call last):
  File "pandas/_libs/tslibs/offsets.pyx", line 6238, in pandas._libs.tslibs.offsets._get_offset
KeyError: 'H'
[omitted: intermediate traceback lines]
ValueError: Invalid frequency: 1H. Failed to parse with error message: ValueError("Invalid frequency: H. Failed to parse with error message: KeyError('H'). Did you mean h?")
```

### 7.5 Legacy environment in a container

The AnomalyDetect repository pins Python 3.6.8 and matching package versions, so its scripts were run unmodified in a container built for those versions.

```text
(.venv) $ docker --version
docker info >/dev/null 2>&1 && echo "DOCKER WORKING" || echo "DOCKER NOT AVAILABLE"
uname -m
Docker version 29.6.1, build 8900f1d
DOCKER NOT AVAILABLE
arm64
(.venv) $ open -a Docker
(.venv) $ docker info >/dev/null 2>&1 && echo "DOCKER WORKING" || echo "DOCKER STILL NOT READY"
DOCKER WORKING
(.venv) $ docker run --rm --platform linux/amd64 python:3.6.8-slim \
  python --version
Unable to find image 'python:3.6.8-slim' locally
3.6.8-slim: Pulling from library/python
[omitted: image download output]
Python 3.6.8
[omitted: Dockerfile creation and image build; the Dockerfile is published as environment/Dockerfile.anomalydetect-py36]
(.venv) $ docker run --rm --platform linux/amd64 rq1-anomalydetect:py36 \
python -c "import sys,numpy,pandas,scipy,statsmodels,sklearn,matplotlib,seaborn; print(sys.version); print('numpy',numpy.__version__); print('pandas',pandas.__version__); print('scipy',scipy.__version__); print('statsmodels',statsmodels.__version__); print('sklearn',sklearn.__version__); print('matplotlib',matplotlib.__version__); print('seaborn',seaborn.__version__)"
3.6.8 (default, Jun 11 2019, 01:21:42)
[GCC 6.3.0 20170516]
numpy 1.18.5
pandas 1.0.4
scipy 1.4.1
statsmodels 0.11.0
sklearn 0.23.1
matplotlib 3.1.0
seaborn 0.10.0
```

### 7.6 HROS-AD and RHRAD in the legacy environment

Both detectors ran to completion. Neither reproduced its committed reference output: none of the 22 generated HROS-AD rows and 20 of the 22 generated RHRAD rows appear in the reference files. The history check shows that the sample input files and the script at the pinned commit are the same blobs as at the commit that added the reference output.

```text
(.venv) $ cd <PROJECT_ROOT>
rm -rf results/gate_a/hrosad_ahyi_docker
mkdir -p results/gate_a/hrosad_ahyi_docker
REF="src/upstream/AnomalyDetect/results/hrosad_offline/HROSAD_anomalies_<participant>.csv"
OUT="results/gate_a/hrosad_ahyi_docker/HROSAD_anomalies_<participant>.csv"
head -n 1 "$REF" > "$OUT"
docker run --rm \
  --platform linux/amd64 \
  -e PYTHONHASHSEED=0 \
  -e TZ=UTC \
  -v "$PWD/src/upstream/AnomalyDetect:/upstream:ro" \
  -v "$PWD/results/gate_a/hrosad_ahyi_docker:/out" \
  rq1-anomalydetect:py36 \
  python /upstream/scripts/hrosad_offline.py \
[omitted: remaining command lines and the generated rows]
[omitted: comparison script]
reference rows: 456
generated rows: 22
reference unique rows: 456
generated unique rows: 22
generated rows appearing somewhere in reference: 0 / 22
reference duplicate rows: 0
reference max repetition of one row: 1
complete generated sequence occurs in reference: False
complete sequence occurrence count: 0
[omitted: generated and reference rows]
[omitted: commands that list the upstream history of the reference output, the sample input files and the script]
=== FILE CREATION COMMIT ===
011935bf66a319a8f3cc5355d13f2306335eef58 2021-02-09 14:19:29 -0800 Add files via upload
=== HR HISTORY ===
6d628ea62079c996d12bfbee8d7bb3aa6d9b81d8 2020-07-17 18:41:28 -0700 Add files via upload
ddd39488a906a24448632b72df403f6c5e7ccb89 2020-07-17 18:36:59 -0700 Delete <participant>_hr.csv
d306a9c2d19b10dbe5f3aa2e1dc87c92bec4cb75 2020-07-17 15:21:34 -0700 Create <participant>_hr.csv
=== STEPS HISTORY ===
6d628ea62079c996d12bfbee8d7bb3aa6d9b81d8 2020-07-17 18:41:28 -0700 Add files via upload
1324bc49d7f9f6b256239602430b3ca78508b123 2020-07-17 18:37:11 -0700 Delete <participant>_steps.csv
46b672d94b16e97d66a53803a2adec5babdd98d1 2020-07-17 15:22:07 -0700 Add files via upload
=== BLOBS AT OUTPUT COMMIT VS PINNED HEAD ===
--- data/<participant>_hr.csv
output-commit:
100644 blob 61f1baa52ef36d7aa794698b8d6951578b8aef93	data/<participant>_hr.csv
pinned-head:
100644 blob 61f1baa52ef36d7aa794698b8d6951578b8aef93	data/<participant>_hr.csv
--- data/<participant>_steps.csv
output-commit:
100644 blob b289443287c786c2c7c175696923ab804c40c6d3	data/<participant>_steps.csv
pinned-head:
100644 blob b289443287c786c2c7c175696923ab804c40c6d3	data/<participant>_steps.csv
=== HROSAD SCRIPT HISTORY ===
37fa5759842c4539f657ebcc160052a8da296895 2021-01-18 12:59:08 -0800 Update hrosad_offline.py
484416a1ef0141befc0ec2a48d0d9e5cab57a6a8 2020-07-20 08:45:45 -0700 Update hrosad_offline.py
ae5ab899f6ff4e837692509e63e672c8aaab7bbd 2020-07-19 12:27:21 -0700 Update hrosad_offline.py
31edd7a32dffd34bbd717a856d1590983db49f03 2020-07-19 12:26:21 -0700 Update hrosad_offline.py
0096da17ee6cd7b3d2fb555a2378194ece139156 2020-07-19 12:25:17 -0700 Update hrosad_offline.py
be1a872aba92482fcb961cb035046ef8d520b02c 2020-07-19 12:25:03 -0700 Update hrosad_offline.py
47a144d7616eac227ea0416ec0837405b2a45e97 2020-07-19 08:20:56 -0700 Update hrosad_offline.py
80f6434dd943db06fa354c34304e14851bc0f90e 2020-07-17 15:42:30 -0700 Update hrosad_offline.py
307c000ce188bed18d495ed3d5792952181e54f3 2020-07-17 15:19:18 -0700 Update hrosad_offline.py
d34c3ffff953b201206c088e88f3def054748139 2020-07-17 14:20:25 -0700 Create hrosad_offline.py
=== HROSAD SCRIPT BLOB COMPARISON ===
output-commit:
100644 blob 0597458433682b49e2e366d430ae4aa9d030541a	scripts/hrosad_offline.py
pinned-head:
100644 blob 0597458433682b49e2e366d430ae4aa9d030541a	scripts/hrosad_offline.py
[omitted: remaining history output]
[omitted: the RHRAD container run, which mirrors the HROS-AD command]
(.venv) $ cd <PROJECT_ROOT>
REF="src/upstream/AnomalyDetect/results/rhrad_offline/RHRAD_anomalies_<participant>.csv"
OUT="results/gate_a/rhrad_ahyi_docker/RHRAD_anomalies_<participant>.csv"
echo "=== ROW COUNTS ==="
wc -l "$REF" "$OUT"
echo "=== GENERATED ROWS PRESENT IN REFERENCE ==="
python - <<'PY'
from pathlib import Path
ref=set(Path("src/upstream/AnomalyDetect/results/rhrad_offline/RHRAD_anomalies_<participant>.csv").read_text().splitlines()[1:])
out=Path("results/gate_a/rhrad_ahyi_docker/RHRAD_anomalies_<participant>.csv").read_text().splitlines()[1:]
print(sum(x in ref for x in out), "/", len(out))
PY
echo "=== EXACT ==="
cmp -s "$REF" "$OUT" && echo PASS || echo FAIL
=== ROW COUNTS ===
     618 src/upstream/AnomalyDetect/results/rhrad_offline/RHRAD_anomalies_<participant>.csv
      23 results/gate_a/rhrad_ahyi_docker/RHRAD_anomalies_<participant>.csv
     641 total
=== GENERATED ROWS PRESENT IN REFERENCE ===
20 / 22
=== EXACT ===
FAIL
```

### 7.7 WearableDetection: exact reproduction

Both committed reference outputs were reproduced byte for byte.

```text
[omitted: R commands that load the upstream functions and write the two outputs]
STATUS=$?
echo "=== EXIT STATUS ==="
echo "$STATUS"
echo "=== STDERR ==="
cat results/gate_a/wearabledetection/stderr.log
echo "=== STDOUT ==="
cat results/gate_a/wearabledetection/stdout.log
if [ "$STATUS" -eq 0 ]; then
  REF1="src/upstream/WearableDetection/result/RHRDiff_offline_detection.csv"
  OUT1="results/gate_a/wearabledetection/RHRDiff_offline_detection.csv"
  REF2="src/upstream/WearableDetection/result/CuSum_online_detection.csv"
  OUT2="results/gate_a/wearabledetection/CuSum_online_detection.csv"
  echo "=== RHR-DIFF ==="
  wc -l "$REF1" "$OUT1"
  shasum -a 256 "$REF1" "$OUT1"
  if cmp -s "$REF1" "$OUT1"; then
    echo "GATE A1 RHR-DIFF: EXACT PASS"
  else
    echo "GATE A1 RHR-DIFF: EXACT REPRODUCTION FAIL"
    diff -u "$REF1" "$OUT1" | head -80
  fi
  echo "=== CUSUM ==="
  wc -l "$REF2" "$OUT2"
  shasum -a 256 "$REF2" "$OUT2"
  if cmp -s "$REF2" "$OUT2"; then
    echo "GATE A1 CUSUM: EXACT PASS"
  else
    echo "GATE A1 CUSUM: EXACT REPRODUCTION FAIL"
    diff -u "$REF2" "$OUT2" | head -80
  fi
fi
echo "=== UPSTREAM STATUS ==="
git -C src/upstream/WearableDetection status --porcelain
=== EXIT STATUS ===
0
=== STDERR ===
Loading required package: zoo
Attaching package: ‘zoo’
The following objects are masked from ‘package:base’:
    as.Date, as.Date.numeric
=== STDOUT ===
RHR-Diff rows: 5
CuSum rows: 3
=== RHR-DIFF ===
       6 src/upstream/WearableDetection/result/RHRDiff_offline_detection.csv
       6 results/gate_a/wearabledetection/RHRDiff_offline_detection.csv
      12 total
15228e284e9a51d2f8b193bac60ea7e59e1dc4ed42f4a4678b9860ace7c5da74  src/upstream/WearableDetection/result/RHRDiff_offline_detection.csv
15228e284e9a51d2f8b193bac60ea7e59e1dc4ed42f4a4678b9860ace7c5da74  results/gate_a/wearabledetection/RHRDiff_offline_detection.csv
GATE A1 RHR-DIFF: EXACT PASS
=== CUSUM ===
       4 src/upstream/WearableDetection/result/CuSum_online_detection.csv
       4 results/gate_a/wearabledetection/CuSum_online_detection.csv
       8 total
6b11ee451a06980d28a18d1ce8926e63e56dc708fd9379bda9db3d4c209cac63  src/upstream/WearableDetection/result/CuSum_online_detection.csv
6b11ee451a06980d28a18d1ce8926e63e56dc708fd9379bda9db3d4c209cac63  results/gate_a/wearabledetection/CuSum_online_detection.csv
GATE A1 CUSUM: EXACT PASS
```

### 7.8 NightSignal and Alarm

Neither repository ships a complete machine-readable reference pair, so each was checked by execution (A2) rather than exact comparison.

```text
(.venv) $ cd <PROJECT_ROOT>
rm -rf results/gate_a/nightsignal_fitbit
mkdir -p results/gate_a/nightsignal_fitbit
docker run --rm \
  --platform linux/amd64 \
  -e TZ=UTC \
  -v "$PWD/src/upstream/wearable-infection:/upstream:ro" \
  -v "$PWD/results/gate_a/nightsignal_fitbit:/out" \
  -w /out \
  rq1-anomalydetect:py36 \
  python /upstream/nightsignal.py \
    --device=Fitbit \
    --restinghr=/upstream/<participant>-Fitbit-rhr.csv \
  > results/gate_a/nightsignal_fitbit/stdout.log \
  2> results/gate_a/nightsignal_fitbit/stderr.log
STATUS=$?
echo "=== EXIT STATUS ==="
echo "$STATUS"
echo "=== STDERR ==="
cat results/gate_a/nightsignal_fitbit/stderr.log
echo "=== GENERATED FILES ==="
find results/gate_a/nightsignal_fitbit -maxdepth 1 -type f \
  -print | sort
echo "=== NS-SIGNALS ==="
if [ -f results/gate_a/nightsignal_fitbit/NS-signals.json ]; then
  cat results/gate_a/nightsignal_fitbit/NS-signals.json
else
  echo "NS-signals.json NOT CREATED"
fi
echo
echo "=== UPSTREAM STATUS ==="
git -C src/upstream/wearable-infection status --porcelain
=== EXIT STATUS ===
0
=== STDERR ===
=== GENERATED FILES ===
results/gate_a/nightsignal_fitbit/NightSignalResult.pdf
results/gate_a/nightsignal_fitbit/NS-signals.json
results/gate_a/nightsignal_fitbit/stderr.log
results/gate_a/nightsignal_fitbit/stdout.log
=== NS-SIGNALS ===
[omitted: per-night signal values]
(.venv) $ cd <PROJECT_ROOT>
Rscript - <<'RS'
source("src/upstream/Alarm/R/online_cusum_alarm_fn.R")
required <- c(
  "online.alarming.fn",
  "stats.track.fn",
  "cusum.detection.fn",
  "rhr.fn",
  "cusum.fn"
)
missing <- required[!vapply(required, exists, logical(1))]
if (length(missing) == 0) {
    cat("GATE A2 ALARM: LOAD/INTERFACE PASS\n")
    for (x in required) {
        cat(x, "(",
            paste(names(formals(get(x))), collapse=", "),
            ")\n", sep="")
    }
} else {
    cat("GATE A2 ALARM: FAIL\n")
    cat("Missing:", paste(missing, collapse=", "), "\n")
    quit(status=1)
}
RS
echo "=== UPSTREAM STATUS ==="
git -C src/upstream/Alarm status --porcelain
Loading required package: zoo
Attaching package: ‘zoo’
The following objects are masked from ‘package:base’:
    as.Date, as.Date.numeric
GATE A2 ALARM: LOAD/INTERFACE PASS
online.alarming.fn(peo.id.1, dir.hr, dir.step, track.par, gap.thres, watch.type, tune.ind, covid.day, plot.shift.day, dat.saved)
stats.track.fn(id, X.rhr.1, base.num, test.r.fixed.1, test.r.1, res.quan.1, pval.thres, resol.tm.1, red.alarm.thres)
cusum.detection.fn(id, test.t, test.t.ind, test.pval, pval.thres, hr.track)
rhr.fn(dat.hr.1, dat.step.1, smth.k.par, rest.min.par, resol.tm.par)
cusum.fn(z.v, test.r)
=== UPSTREAM STATUS ===
```

### 7.9 Machine-readable Gate A record

The first call failed because the script was not where the command expected it; the second wrote the record published as results/gate_a/gate_a_results.json.

```text
(.venv) $ python <DOWNLOADS>/rebuild_gate_a.py
/opt/homebrew/Cellar/python@3.14/3.14.1/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python: can't open file '<DOWNLOADS>/rebuild_gate_a.py': [Errno 2] No such file or directory
(.venv) $ python <DOWNLOADS>/rebuild_gate_a.py
JSON VALID
FILE: <PROJECT_ROOT>/results/gate_a/gate_a_results.json
STATUS: COMPLETE_WITH_MIXED_REPRODUCTION
SIX STATUSES
RHR-Diff | execution = PASS | exact = PASS
CuSum | execution = PASS | exact = PASS
HROS-AD | execution = PASS | exact = FAIL
RHRAD | execution = PASS | exact = FAIL
NightSignal Fitbit | execution = PASS | exact = N/A
Alarm online CuSum | execution = PASS | exact = N/A
```

## 8. Published-table audit: Gate B

### 8.1 Source search and an interrupted cell search

The counts behind the published alert-day specificity were searched for in the supplementary files. The text search matched only unrelated numbers. A cell-by-cell workbook search was then stopped by hand; the partial output it had written is not published.

```text
(.venv) $ grep -A20 '=== ALAVI STRUCTURAL SUMMARY ===' \
<PROJECT_ROOT>/results/gate_b_table_extract.txt
=== ALAVI STRUCTURAL SUMMARY ===
Fig4A participant rows: 66
Fig4A numeric alert offsets: 58
Fig4A <= 0: 53
Fig4A < 0: 37
Fig4A == 0: 16
Fig4A > 0: 5
Fig4A missing/non-numeric: 8
Fig4B participant rows: 18
Fig4B numeric alert offsets: 14
Fig4B <= 0: 14
Fig4B < 0: 12
Fig4B == 0: 2
Fig4B > 0: 0
Fig4B missing/non-numeric: 4
Combined participant rows: 84
Combined numeric alert offsets: 72
Combined <= 0: 67
Combined < 0: 49
Combined == 0: 18
Combined > 0: 5
(.venv) $ cd <PROJECT_ROOT>
echo "=== TEXT FILE SEARCH ==="
grep -RInE '87124|87,124|12186|12,186|87\.7' \
  metadata src results \
  --exclude='*.xlsx' \
  --exclude='*.zip' \
  --exclude='gate_reproduction.py' \
  2>/dev/null | head -100
echo
echo "=== XLSX INTERNAL SEARCH ==="
for f in metadata/*.xlsx; do
    echo "--- $f"
    unzip -p "$f" 2>/dev/null | \
      grep -Eo '87124|12186|87\.7' | sort -u
done
=== TEXT FILE SEARCH ===
[omitted: matches inside the upstream sample heart-rate and step files and one participant-level project output; they are unrelated numbers]
results/power_sim_frozen_n38.json:4676:      "mean_discordant": 24.871249999999996,
=== XLSX INTERNAL SEARCH ===
--- metadata/phase1_supplementary_data.xlsx
12186
87.7
87124
--- metadata/phase2_covid_metadata.xlsx
(.venv) $ python <DOWNLOADS>/locate_gate_b_specificity_cells.py \
> <PROJECT_ROOT>/results/gate_b_specificity_cell_audit.txt
<PROJECT_ROOT>/.venv/lib/python3.14/site-packages/openpyxl/worksheet/_reader.py:329: UserWarning: Unknown extension is not supported and will be removed
  warn(msg)
^CTraceback (most recent call last):
  File "<DOWNLOADS>/locate_gate_b_specificity_cells.py", line 46, in <module>
    vv = ws.cell(rr, cc).value
         ~~~~~~~^^^^^^^^
  File "<PROJECT_ROOT>/.venv/lib/python3.14/site-packages/openpyxl/worksheet/worksheet.py", line 244, in cell
    cell = self._get_cell(row, column)
  File "<PROJECT_ROOT>/.venv/lib/python3.14/site-packages/openpyxl/worksheet/_read_only.py", line 132, in _get_cell
    for row in self._cells_by_row(column, row, column, row):
               ~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<PROJECT_ROOT>/.venv/lib/python3.14/site-packages/openpyxl/worksheet/_read_only.py", line 85, in _cells_by_row
    for idx, row in parser.parse():
                    ~~~~~~~~~~~~^^
  File "<PROJECT_ROOT>/.venv/lib/python3.14/site-packages/openpyxl/worksheet/_reader.py", line 156, in parse
    for _, element in it:
                      ^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/xml/etree/ElementTree.py", line 1251, in iterator
    pullparser.feed(data)
    ~~~~~~~~~~~~~~~^^^^^^
  File "/opt/homebrew/Cellar/python@3.14/3.14.1/Frameworks/Python.framework/Versions/3.14/lib/python3.14/xml/etree/ElementTree.py", line 1301, in feed
    self._parser.feed(data)
    ~~~~~~~~~~~~~~~~~^^^^^^
KeyboardInterrupt
```

### 8.2 Gate B computation and its tests

Six published quantities were reconstructed. The alert-day specificity was recorded as not reconstructible from the public tables.

```text
(.venv) $ python <DOWNLOADS>/install_gate_b.py
Wrote: <PROJECT_ROOT>/src/gate_b_compute.py
Wrote: <PROJECT_ROOT>/tests/test_reproduction.py
Running Gate B computation...
{
  "gate": "B",
  "status": "COMPLETE_WITH_ONE_PUBLIC_DATA_LIMITATION",
  "observed": {
    "mishra_analysed_cases": 32,
    "mishra_detected": 26,
    "mishra_median_lead_days_vs_onset": 4.0,
    "mishra_detected_at_or_before_onset_of_25": 22,
    "alavi_confirmed_positives": 84,
    "alavi_sensitivity_per_person_pct": 79.76190476190476
  },
  "mishra_detail": {
    "analysed_cases": 32,
    "detected_cases_groups_I_II": 26,
    "symptom_information_cases_among_detected": 25,
    "rhrdiff_numeric_symptom_deltas": 24,
    "detected_at_or_before_onset": 22,
    "median_lead_days_vs_onset": 4.0,
    "median_signed_delta_days": -4.0,
    "participant_ids": [
[omitted: 32 participant identifiers; the list is also removed from the published copy of results/gate_b_results.json]
    ],
    "source": "phase1_supplementary_data.xlsx::SuppTable13_Fig4abc",
    "interpretation": "Groups I and II are the 26 detected cases described in the paper. 'NaN' denotes unavailable symptom/diagnosis date; 'miss' denotes an algorithm miss and is therefore not converted into a numeric RHR-Diff delta."
  },
  "alavi_detail": {
    "confirmed_positives": 84,
    "symptomatic_rows": 66,
    "asymptomatic_rows": 18,
    "symptomatic_at_or_before_onset": 53,
    "asymptomatic_at_or_before_test": 14,
    "true_positive_participants": 67,
    "sensitivity_per_person_pct": 79.76190476190476,
    "fig4_union_matches_positive_cohort": true,
    "duplicate_alert_ids": [],
    "source": "phase2_covid_metadata.xlsx::SourceData_COVID19_Positives + SourceData_Fig4A_Presymp + SourceData_Fig4B_Asymp"
  },
  "report": {
    "mishra_analysed_cases": {
      "status": "PASS",
      "observed": 32,
      "published": 32,
      "tol": 0
    },
    "mishra_detected": {
      "status": "PASS",
      "observed": 26,
      "published": 26,
      "tol": 2
    },
    "mishra_median_lead_days_vs_onset": {
      "status": "PASS",
      "observed": 4.0,
      "published": 4,
      "tol": 1
    },
    "mishra_detected_at_or_before_onset_of_25": {
      "status": "PASS",
      "observed": 22,
      "published": 22,
      "tol": 2
    },
    "alavi_confirmed_positives": {
      "status": "PASS",
      "observed": 84,
      "published": 84,
      "tol": 0
    },
    "alavi_sensitivity_per_person_pct": {
      "status": "PASS",
      "observed": 79.76190476190476,
      "published": 80.0,
      "tol": 5.0,
      "denominator": "67/84 participants"
    },
    "alavi_specificity_per_alert_day_pct": {
      "status": "NOT_RECONSTRUCTIBLE_PUBLIC_DATA",
      "published": 87.7,
      "tol": 2.0,
      "published_numerator_TN": 87124,
      "published_denominator_TN_plus_FP": 99310,
      "published_false_positive_alert_days": 12186,
      "published_arithmetic_pct": 87.72933239351525,
      "reason": "The public Source Data workbook supplied here covers COVID-positive participants and alert timing, but does not provide the non-COVID participant-day alert labels and negative-test/untested survey timing needed to independently reconstruct TN=87,124 and FP=12,186. The values are retained as a paper-reported benchmark, not counted as a reproduced statistic."
    },
    "_policy": "A failing gate is reported as a finding. Upstream code is NOT modified to close it. Schedule comparisons are then anchored to our own S1 reference arm, which is internally valid regardless. The two Alavi figures are reported with their denominators named and never as a matched sensitivity/specificity pair."
  },
  "decision": "Six preregistered quantities are independently reconstructed from participant-level public source tables. Alavi alert-day specificity is not labelled PASS or FAIL because the public source package used here lacks the denominator-level non-COVID alert/survey labels needed for independent reconstruction."
}
Running reproduction tests...
.......                                                                                                                                                                                                 [100%]
7 passed in 0.09s
DONE
Result: <PROJECT_ROOT>/results/gate_b_results.json
```

## 9. Timestamp warning audit and calibration reporting

### 9.1 Timestamp warning audit

The date-parsing warning seen during the Phase 2 inventory was traced to one file.

```text
(.venv) $ python <DOWNLOADS>/audit_phase2_timestamp_warning.py
ZIP: <PROJECT_ROOT>/data_raw/COVID-19-Phase2-Wearables.zip
SIZE_GB: 5.157
HR MEMBERS: 2123
FINDING: COVID-19-Phase2-Wearables/<participant>/Orig_NonFitbit_HR.csv
 ERROR: RuntimeError: no timestamp column found; columns were ['Error in query string: Error processing job']
FINDING: COVID-19-Phase2-Wearables/<participant>/Orig_NonFitbit_HR.csv
 WARNING: Could not infer format, so each element will be parsed individually, falling back to `dateutil`. To ensure parsing is consistent and as-expected, please specify a format.
=== SUMMARY ===
checked: 2123
findings: 2
output: <PROJECT_ROOT>/results/phase2_timestamp_warning_audit.json
First finding: COVID-19-Phase2-Wearables/<participant>/Orig_NonFitbit_HR.csv
```

### 9.2 Calibration-minimum reporting patch

The record of the calibration-minimum choice was extended to state that the prespecified fallback had been invoked. A copy of the script was kept before the patch.

```text
(.venv) $ python <DOWNLOADS>/patch_calibration_reporting.py
Patched: <PROJECT_ROOT>/src/calibration_resolution.py
Wrote test: <PROJECT_ROOT>/tests/test_calibration_resolution.py
Updated record: <PROJECT_ROOT>/results/calibration_rule.json
..                                                                                                                                                                                                      [100%]
2 passed in 0.06s
=== CALIBRATION RECORD ===
chosen_C_min: 28
retention_at_choice: 0.7755102040816326
floor: 0.8
fallback_invoked: True
fallback_value: 28
retention_floor_met: False
note: availability-only rule; frozen before any outcome inspection; no candidate minimum met the 0.80 retention floor, so the prespecified fallback C_min=28 was invoked
(.venv) $ cd <PROJECT_ROOT>
pytest -q
echo "=== GIT STATUS ==="
git status --short
echo "=== CURRENT COMMIT ==="
git rev-parse HEAD
............................................................................................................................................                                                            [100%]
140 passed in 22.02s
=== GIT STATUS ===
fatal: not a git repository (or any of the parent directories): .git
=== CURRENT COMMIT ===
fatal: not a git repository (or any of the parent directories): .git
```

## 10. Pre-outcome checkpoint

### 10.1 Checkpoint commit

The project repository was initialized at this point, before any schedule-performance outcome was inspected.

```text
(.venv) $ cd <PROJECT_ROOT>
cat >> .gitignore <<'EOF'
# Pre-patch / obsolete local snapshots
*_before_*.py
*.pre_reporting_patch
*.pre_gate_b_backup
results/gate_a/gate_a_results_PRELIMINARY_DO_NOT_USE.json
EOF
git rm --cached --ignore-unmatch \
  src/*_before_*.py \
  src/*.pre_reporting_patch \
  src/*.pre_gate_b_backup \
  results/gate_a/gate_a_results_PRELIMINARY_DO_NOT_USE.json
cat > docs/PRE_OUTCOME_CHECKPOINT.md <<'EOF'
# Pre-outcome checkpoint
Date: 2026-09-01
This root Git repository was initialized after completion of the data,
cohort, power, and reproduction preparation work, but before inspection
of schedule-performance outcomes.
Checkpoint status:
- Full regression suite: 140 tests passed.
- Final primary base cohort: N=38.
- C_min=28 selected using the prespecified availability-only fallback.
- Retention at C_min: 0.7755102041; 0.80 floor not met.
- Gate A: complete with mixed reproduction.
- Gate B: six published quantities independently reconstructed.
- Alavi 87.7% alert-day specificity retained as a published benchmark;
  not independently reconstructible from the available public source tables.
- Phase-2 malformed <participant> HR file quarantined.
- Phase-2 timestamp warning isolated to <participant>; all sampled timestamps
  parsed, and native interval calculations sort timestamps before differences.
- No schedule-performance outcomes had been inspected at this checkpoint.
EOF
git add .
pytest -q
git commit -m "pre-outcome data and reproduction checkpoint"
echo "=== CHECKPOINT ==="
git log -1 --oneline
git status --short
zsh: no matches found: src/*.pre_gate_b_backup
............................................................................................................................................                                                            [100%]
140 passed in 21.87s
[master (root-commit) 990f97e] pre-outcome data and reproduction checkpoint
 130 files changed, 54910 insertions(+)
[omitted: list of the 130 committed files]
=== CHECKPOINT ===
990f97e (HEAD -> master) pre-outcome data and reproduction checkpoint
```

## 11. Energy design

### 11.1 Hardware protocol, then amendment A4

The bench protocol was committed and then superseded by the modelled-energy design; it was never executed. The login banner reports the previous login, so it does not date the commands after it.

```text
(.venv) $ cp <DOWNLOADS>/hardware_measurement_protocol_v1.md <PROJECT_ROOT>/hardware/measurement_protocol.md
(.venv) $ cd <PROJECT_ROOT>
git add hardware/measurement_protocol.md
git commit -m "freeze hardware energy measurement protocol"
[master ee7c110] freeze hardware energy measurement protocol
 1 file changed, 249 insertions(+), 69 deletions(-)
(.venv) $

Last login: Wed Sep  2 10:51:35 on ttys000
$ cp <DOWNLOADS>/prereg-v1.2-amendment-A4-no-hardware.md <PROJECT_ROOT>/docs/
cd <PROJECT_ROOT>
git add docs/prereg-v1.2-amendment-A4-no-hardware.md
git commit -m "amend preregistration to modelled energy design"
[master 279d7e4] amend preregistration to modelled energy design
 1 file changed, 158 insertions(+)
 create mode 100644 docs/prereg-v1.2-amendment-A4-no-hardware.md
```

### 11.2 Energy-match audit and freeze

```text
$ cd <PROJECT_ROOT>
source .venv/bin/activate
python <DOWNLOADS>/finalize_modelled_energy_preoutcome.py
Running energy-match audit...
=== LOW ===
S1 reference: 5953.847488 J
E1 target=1190.769498 J
  S2  N=29 achieved=1199.114552 J err=+0.701% FEASIBLE_WITHIN_5PCT
  S3  N=29 achieved=1199.114552 J err=+0.701% FEASIBLE_WITHIN_5PCT
  S5  N=29 achieved=1199.114552 J err=+0.701% FEASIBLE_WITHIN_5PCT
  S4  N=29 achieved=1201.439072 J err=+0.896% FEASIBLE_WITHIN_5PCT
  S3r N=29 achieved=1201.439072 J err=+0.896% FEASIBLE_WITHIN_5PCT
  S6  N=29 achieved=1201.439072 J err=+0.896% FEASIBLE_WITHIN_5PCT
E2 target=595.384749 J
  S2  N=14 achieved=578.893982 J err=-2.770% FEASIBLE_WITHIN_5PCT
  S3  N=14 achieved=578.893982 J err=-2.770% FEASIBLE_WITHIN_5PCT
  S5  N=14 achieved=578.893982 J err=-2.770% FEASIBLE_WITHIN_5PCT
  S4  N=14 achieved=581.515502 J err=-2.329% FEASIBLE_WITHIN_5PCT
  S3r N=14 achieved=581.515502 J err=-2.329% FEASIBLE_WITHIN_5PCT
  S6  N=14 achieved=581.515502 J err=-2.329% FEASIBLE_WITHIN_5PCT
E3 target=297.692374 J
  S2  N= 7 achieved=289.457716 J err=-2.766% FEASIBLE_WITHIN_5PCT
  S3  N= 7 achieved=289.457716 J err=-2.766% FEASIBLE_WITHIN_5PCT
  S5  N= 7 achieved=289.457716 J err=-2.766% FEASIBLE_WITHIN_5PCT
  S4  N= 7 achieved=292.217836 J err=-1.839% FEASIBLE_WITHIN_5PCT
  S3r N= 7 achieved=292.217836 J err=-1.839% FEASIBLE_WITHIN_5PCT
[omitted: remaining scenario and budget lines; the complete audit is published as results/modelled_energy_match_audit.json]
PRIMARY E3 ALL SCENARIOS FEASIBLE: True
Wrote: <PROJECT_ROOT>/results/modelled_energy_match_audit.json
Running new tests...
...                                                                                                                                                                                                     [100%]
3 passed in 0.02s
Running full suite...
...............................................................................................................................................                                                         [100%]
143 passed in 21.89s
DONE
Do not commit until the audit output has been reviewed.
[omitted: review of the audit output]
(.venv) $ cd <PROJECT_ROOT>
# Remove obsolete uncommitted draft if present
rm -f docs/modelled_energy_parameter_provenance_DRAFT.md
rm -f docs/modelled_energy_parameter_provenance_PRE_FREEZE_DRAFT.md
git add \
  docs/modelled_energy_parameter_provenance.md \
  docs/prereg-v1.2-amendment-A4-no-hardware.md \
  configs/modelled_energy_scenarios.json \
  src/energy_model.py \
  src/modelled_energy_match.py \
  tests/test_modelled_energy_freeze.py \
  results/modelled_energy_match_audit.json
git commit -m "freeze pre-outcome modelled energy parameters and budgets"
echo "=== ENERGY FREEZE ==="
git log -1 --oneline
echo "=== STATUS ==="
git status --short
zsh: command not found: #
[master 4023717] freeze pre-outcome modelled energy parameters and budgets
 7 files changed, 1024 insertions(+), 6 deletions(-)
 create mode 100644 configs/modelled_energy_scenarios.json
 create mode 100644 docs/modelled_energy_parameter_provenance.md
 create mode 100644 results/modelled_energy_match_audit.json
 create mode 100644 src/modelled_energy_match.py
 create mode 100644 tests/test_modelled_energy_freeze.py
=== ENERGY FREEZE ===
4023717 (HEAD -> master) freeze pre-outcome modelled energy parameters and budgets
=== STATUS ===
```

## 12. Primary runner and executions

### 12.1 Runner freeze (A5)

```text
(.venv) $ cd <PROJECT_ROOT>
cp <DOWNLOADS>/primary_e3_experiment.py src/
cp <DOWNLOADS>/test_primary_e3_experiment.py tests/
cp <DOWNLOADS>/prereg-v1.2-amendment-A5-runner-operationalization.md docs/
pytest tests/test_primary_e3_experiment.py -q
pytest -q
python src/primary_e3_experiment.py --preflight
git diff --check
git status --short
......                                                                                                                                                                                                  [100%]
6 passed in 0.84s
.....................................................................................................................................................                                                   [100%]
149 passed in 21.97s
PRE-FLIGHT PASS
  frozen cohort: N=38
  E3 LOW/CENTRAL/HIGH: all arms feasible at N=7
  burst length: 10 minutes
  alert budget: <=2 alert-days/person-month
  pair calibration floor: 16 z-defined days
  raw ZIPs present
?? docs/prereg-v1.2-amendment-A5-runner-operationalization.md
?? src/primary_e3_experiment.py
?? tests/test_primary_e3_experiment.py
(.venv) $ cd <PROJECT_ROOT>
git add \
  docs/prereg-v1.2-amendment-A5-runner-operationalization.md \
  src/primary_e3_experiment.py \
  tests/test_primary_e3_experiment.py
git commit -m "freeze primary E3 experiment runner before outcomes"
git log -1 --oneline
git status --short
[master d1d5265] freeze primary E3 experiment runner before outcomes
 3 files changed, 950 insertions(+)
 create mode 100644 docs/prereg-v1.2-amendment-A5-runner-operationalization.md
 create mode 100644 src/primary_e3_experiment.py
 create mode 100644 tests/test_primary_e3_experiment.py
d1d5265 (HEAD -> master) freeze primary E3 experiment runner before outcomes
```

### 12.2 First real-data execution

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python src/primary_e3_experiment.py --run-real
PRE-FLIGHT PASS
  frozen cohort: N=38
  E3 LOW/CENTRAL/HIGH: all arms feasible at N=7
  burst length: 10 minutes
  alert budget: <=2 alert-days/person-month
  pair calibration floor: 16 z-defined days
  raw ZIPs present
[omitted: 38 per-participant progress lines]
REAL RUN COMPLETE
Outcome files: <PROJECT_ROOT>/results/primary_e3_run_d1d5265
No scientific outcome values were printed.
```

### 12.3 Quality-control audit of the first execution

This audit prints structure and quality-control summaries only. The low calibration-floor and evaluability counts led to the input diagnostic below.

```text
(.venv) $ cd <PROJECT_ROOT>
python <DOWNLOADS>/audit_primary_e3_qc_only.py
=== MANIFEST ===
git_commit: d1d526536ea220be88a5d972c913de940d47aa02
energy_freeze_commit: 4023717
scenario/budget: CENTRAL E3
N_budget / burst_minutes: 7 10
frozen cohort: 38
=== ARM OUTCOME TABLE STRUCTURE ===
rows: 266 (expected 266)
unique participants: 38
rows per arm:
arm
S1     38
S2     38
S3     38
S5     38
S4     38
S3r    38
S6     38
=== CALIBRATION QC (NO DETECTION RESULTS) ===
      n  floor_met  cal_days_min  cal_days_median  cal_days_max  saturated
arm
S1   38          5             0              0.0           381          0
S2   38          5             0              0.0           381          0
S3   38          5             0              0.0           380          0
S5   38          5             0              0.0           381          0
S4   38          5             0              0.0           380          0
S3r  38          5             0              0.0           380          0
S6   38          5             0              0.0           381          0
alert-budget violations: 0
=== PRESYMPTOMATIC EVALUABILITY QC ===
     participants  zero_evaluable_days  eval_days_min  eval_days_median  eval_days_max
arm
S1             38                   33              0               0.0             21
S2             38                   33              0               0.0             21
S3             38                   33              0               0.0             21
S5             38                   33              0               0.0             21
S4             38                   33              0               0.0             21
S3r            38                   33              0               0.0             21
S6             38                   33              0               0.0             21
=== SCHEDULE DELIVERY QC ===
non-S1 daily rows with n_scheduled > n_requested: 0
daily rows with delivered_minutes > scheduled_minutes: 0
     event_sched_min_median  event_deliv_min_median  event_deliv_min_min  event_days_with_delivery_median
arm
S1                  30240.0                 28700.5                18898                             21.0
S2                   1470.0                  1386.0                  948                             21.0
S3                   1470.0                  1437.5                 1062                             21.0
S5                   1470.0                  1399.5                  923                             21.0
S4                      0.0                     0.0                    0                              0.0
S3r                     0.0                     0.0                    0                              0.0
S6                      0.0                     0.0                    0                              0.0
=== M1 FEASIBILITY QC ===
participants with >40% unavailable M1 event-days: 28
M1 unavailable fraction median: 1.0
M1 unavailable fraction max: 1.0
=== PAIR FILE STRUCTURE ONLY ===
rows: 152 (expected 152)
comparisons: ['H1', 'H2', 'H3', 'M1']
rows per comparison:
comparison
H1    38
H2    38
H3    38
M1    38
=== QC RESULT ===
PASS — structural/QC audit completed.
No H1/M1/H2/H3 win-loss counts, detection rates, or warning-time results were printed.
```

### 12.4 Input diagnostic

Outcome-blind. It showed that Phase 2 step records carry no explicit zero rows, unlike Phase 1.

```text
(.venv) $ cd <PROJECT_ROOT>
python <DOWNLOADS>/diagnose_primary_e3_input_alignment.py
[omitted: 38 per-participant progress lines]
=== INPUT ALIGNMENT DIAGNOSTIC ===
participants: 38
onset inside HR range: 38 / 38
onset inside step range: 38 / 38
median all-data zero-step fraction: 0.0
median step gap (min): 1.0
median step p95 gap (min): 13.0
median event HR unique minutes: 28700.5
median event recorded step minutes: 6174.0
median event zero-step minutes: 0.0
median event HR rows with a step record: 52204.5
median event HR rows with zero-step: 0.0
participants with >=1 event day having >=5 HR rows at zero-step minutes: 10 / 38
=== PHASE SUMMARY ===
        step_zero_fraction_all  step_gap_median_min  event_hr_unique_minutes  event_step_recorded_minutes  event_zero_step_minutes  event_hr_rows_with_step_record  event_hr_rows_with_zero_step  event_days_with_5plus_zero_step_hr
phase
phase1                   0.824                  1.0                  29009.0                      30240.0                  25015.5                        210036.0                      156312.5                                21.0
phase2                   0.000                  1.0                  28331.0                       5746.5                      0.0                         45654.5                           0.0                                 0.0
[omitted: per-participant flag table]
Wrote: <PROJECT_ROOT>/results/primary_e3_input_diagnostic.csv
This diagnostic does not read or print any H1/M1/H2/H3 detection outcome.
```

### 12.5 Correction (A6) and corrected execution

```text
(.venv) $ cd <PROJECT_ROOT>
python <DOWNLOADS>/apply_A6_phase2_sparse_steps.py
pytest tests/test_phase2_sparse_step_semantics.py -q
pytest -q
python <DOWNLOADS>/diagnose_primary_e3_input_alignment.py
git diff --check
git status --short
PATCH APPLIED
Modified: <PROJECT_ROOT>/src/primary_e3_experiment.py
Created : <PROJECT_ROOT>/tests/test_phase2_sparse_step_semantics.py
Created : <PROJECT_ROOT>/docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md
Do not use --run-real yet.
.....                                                                                                                                                                                                   [100%]
5 passed in 0.52s
..........................................................................................................................................................                                              [100%]
154 passed in 21.98s
[omitted: re-run of the input diagnostic (per-participant progress and flag lines)]
 M src/primary_e3_experiment.py
?? docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md
?? results/primary_e3_input_diagnostic.csv
?? results/primary_e3_run_d1d5265/
?? tests/test_phase2_sparse_step_semantics.py
(.venv) $ cd <PROJECT_ROOT>
pytest tests/test_phase2_sparse_step_semantics.py -q
pytest -q
python src/primary_e3_experiment.py --preflight
git diff --check
printf '\nresults/primary_e3_run_d1d5265/\nresults/primary_e3_input_diagnostic.csv\n' >> .git/info/exclude
git status --short
.....                                                                                                                                                                                                   [100%]
5 passed in 0.46s
..........................................................................................................................................................                                              [100%]
154 passed in 21.60s
PRE-FLIGHT PASS
  frozen cohort: N=38
  E3 LOW/CENTRAL/HIGH: all arms feasible at N=7
  burst length: 10 minutes
  alert budget: <=2 alert-days/person-month
  pair calibration floor: 16 z-defined days
  raw ZIPs present
 M src/primary_e3_experiment.py
?? docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md
?? tests/test_phase2_sparse_step_semantics.py
(.venv) $ cd <PROJECT_ROOT>
git add \
  src/primary_e3_experiment.py \
  docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md \
  tests/test_phase2_sparse_step_semantics.py
git commit -m "correct Phase2 sparse step semantics before outcome inspection"
git log -1 --oneline
git status --short
[master 83cc8d1] correct Phase2 sparse step semantics before outcome inspection
 3 files changed, 187 insertions(+)
 create mode 100644 docs/prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md
 create mode 100644 tests/test_phase2_sparse_step_semantics.py
83cc8d1 (HEAD -> master) correct Phase2 sparse step semantics before outcome inspection
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python src/primary_e3_experiment.py --run-real
PRE-FLIGHT PASS
  frozen cohort: N=38
  E3 LOW/CENTRAL/HIGH: all arms feasible at N=7
  burst length: 10 minutes
  alert budget: <=2 alert-days/person-month
  pair calibration floor: 16 z-defined days
  raw ZIPs present
[omitted: 38 per-participant progress lines]
REAL RUN COMPLETE
Outcome files: <PROJECT_ROOT>/results/primary_e3_run_83cc8d1
No scientific outcome values were printed.
```

### 12.6 Quality-control audit of the corrected execution

```text
(.venv) $ cd <PROJECT_ROOT>
python <DOWNLOADS>/audit_primary_e3_corrected_qc_only.py
=== MANIFEST ===
git_commit: 83cc8d1f1e6711fefd8c52954f9f5d33c93fc1f3
energy_freeze_commit: 4023717
scenario: CENTRAL
budget: E3
N_budget: 7
burst_minutes: 10
n_frozen_cohort: 38
phase2_step_semantics: At minute resolution, infer steps=0 only for Phase-2 Fitbit HR-observed minutes with no explicit step-file record; explicit step records win; minutes with neither HR nor steps remain unknown.
=== TABLE STRUCTURE ===
arm_outcomes rows: 266 expected 266
unique participants: 38
rows per arm:
arm
S1     38
S2     38
S3     38
S5     38
S4     38
S3r    38
S6     38
=== A6 INPUT-SEMANTICS QC ===
phase2 participants: 28
phase1 participants: 10
phase2 semantics applied: 28 / 28
phase1 semantics applied: 0 / 10
phase2 inferred-zero minutes median: 214578.5
phase1 inferred-zero minutes total: 0
=== CALIBRATION QC — NO DETECTION RESULTS ===
      n  floor_met  cal_days_min  cal_days_median  cal_days_max  saturated
arm
S1   38         32             4             27.0           381          0
S2   38         32             4             27.0           381          0
S3   38         30             3             26.0           380          0
S5   38         32             4             27.0           381          0
S4   38         32             3             26.5           380          0
S3r  38         30             3             25.5           380          0
S6   38         30             4             25.5           381          0
alert-budget violations: 0
=== PRESYMPTOMATIC EVALUABILITY QC — NO DETECTION RESULTS ===
     participants  zero_evaluable_days  eval_days_min  eval_days_median  eval_days_max
arm
S1             38                    6              0              21.0             21
S2             38                    6              0              21.0             21
S3             38                    8              0              20.0             21
S5             38                    6              0              21.0             21
S4             38                    6              0              21.0             21
S3r            38                    8              0              20.0             21
S6             38                    8              0              20.0             21
=== SCHEDULE DELIVERY QC ===
rows with n_scheduled > n_requested: 0
rows with delivered_minutes > scheduled_minutes: 0
     event_sched_min_median  event_deliv_min_median  event_deliv_min_min  event_days_with_delivery_median
arm
S1                  30240.0                 28700.5                18898                             21.0
S2                   1470.0                  1386.0                  948                             21.0
S3                   1470.0                  1437.5                 1062                             21.0
S5                   1470.0                  1399.5                  923                             21.0
S4                   1470.0                  1458.5                 1186                             21.0
S3r                  1470.0                  1403.0                  730                             21.0
S6                   1470.0                  1396.5                  730                             21.0
=== M1 FEASIBILITY QC ===
participants with >40% unavailable M1 event-days: 0
M1 unavailable fraction median: 0.0
M1 unavailable fraction max: 0.238095238095238
=== PAIR FILE STRUCTURE ONLY ===
rows: 152 expected 152
comparisons: ['H1', 'H2', 'H3', 'M1']
rows per comparison:
comparison
H1    38
H2    38
H3    38
M1    38
=== CORRECTED-RUN QC RESULT ===
PASS — corrected-run structural/input/QC audit completed.
No H1/M1/H2/H3 win-loss counts, detection rates, warning times, p-values, or effect sizes were printed.
```

## 13. Confirmatory analysis

### 13.1 Confirmatory reveal

The first reveal script failed in its printed summary; the second version, which differs in that one line, completed. Both are published in evidence/scripts/.

```text
(.venv) $ cd <PROJECT_ROOT>
python <DOWNLOADS>/reveal_primary_e3_confirmatory_results.py
=== PREREGISTERED CONFIRMATORY ANALYSIS ===
Corrected run commit: 83cc8d1f1e6711fefd8c52954f9f5d33c93fc1f3
Primary test: exact binomial sign test on W vs L, two-sided alpha=0.05
Effect: theta=(W+0.5*T)/N; 95% BCa bootstrap, 10,000 participant resamples
--- H1: S3 vs S2 ---
Traceback (most recent call last):
  File "<DOWNLOADS>/reveal_primary_e3_confirmatory_results.py", line 267, in <module>
    f"N={int(row.N_pair)} | W/L/T={int(row.W)}/{int(row.L)}/{int(row.T)} "
                                                             ~~~^^^^^^^
TypeError: int() argument must be a string, a bytes-like object or a real number, not 'Series'
(.venv) $ cd <PROJECT_ROOT>
python <DOWNLOADS>/reveal_primary_e3_confirmatory_results_fixed.py
=== PREREGISTERED CONFIRMATORY ANALYSIS ===
Corrected run commit: 83cc8d1f1e6711fefd8c52954f9f5d33c93fc1f3
Primary test: exact binomial sign test on W vs L, two-sided alpha=0.05
Effect: theta=(W+0.5*T)/N; 95% BCa bootstrap, 10,000 participant resamples
--- H1: S3 vs S2 ---
N=30 | W/L/T=8/12/10 | discordant=20
theta=0.433 (95% BCa 0.300 to 0.583) | W/L ratio=0.667
exact two-sided p=0.5034
S3: detection 19/30 (63.3%)
S3: warning among detected median 13.0 d (IQR 9.0–19.5)
S2: detection 20/30 (66.7%)
S2: warning among detected median 14.0 d (IQR 8.2–19.0)
CONFIRMATORY STATUS: NOT REJECTED.
--- M1: S3r vs S6 ---
N=30 | W/L/T=13/11/6 | discordant=24
theta=0.533 (95% BCa 0.367 to 0.683) | W/L ratio=1.182
exact two-sided p=0.8388
S3r: detection 23/30 (76.7%)
S3r: warning among detected median 13.0 d (IQR 5.0–16.5)
S6: detection 19/30 (63.3%)
S6: warning among detected median 9.0 d (IQR 5.5–16.5)
CONFIRMATORY STATUS: NOT TESTED — preceding fixed-sequence gate closed.
The numerical estimate/p-value above is descriptive/estimation-only.
--- H2: S3 vs S5 ---
N=30 | W/L/T=10/10/10 | discordant=20
theta=0.500 (95% BCa 0.350 to 0.650) | W/L ratio=1.000
exact two-sided p=1.0000
S3: detection 19/30 (63.3%)
S3: warning among detected median 13.0 d (IQR 9.0–19.5)
S5: detection 19/30 (63.3%)
S5: warning among detected median 14.0 d (IQR 9.0–17.5)
CONFIRMATORY STATUS: NOT TESTED — preceding fixed-sequence gate closed.
The numerical estimate/p-value above is descriptive/estimation-only.
--- H3: S3 vs S4 ---
N=30 | W/L/T=2/9/19 | discordant=11
theta=0.383 (95% BCa 0.283 to 0.483) | W/L ratio=0.222
exact two-sided p=0.0654
S3: detection 19/30 (63.3%)
S3: warning among detected median 13.0 d (IQR 9.0–19.5)
S4: detection 22/30 (73.3%)
S4: warning among detected median 15.5 d (IQR 10.0–19.8)
CONFIRMATORY STATUS: NOT TESTED — preceding fixed-sequence gate closed.
The numerical estimate/p-value above is descriptive/estimation-only.
=== FIXED-SEQUENCE GATEKEEPING ===
H1 rejected: False
H1 theta > 0.5: False
Stage-2 gate open: False
M1 confirmatorily tested: False
Stage-3 gate open: False
H2/H3 Holm applied: False
Saved:
<PROJECT_ROOT>/results/primary_e3_run_83cc8d1/confirmatory_analysis/confirmatory_comparison_summary.csv
<PROJECT_ROOT>/results/primary_e3_run_83cc8d1/confirmatory_analysis/gatekeeping_decisions.json
```

## 14. Post-primary sensitivity analysis

### 14.1 Sensitivity plan freeze (A7)

Written after the confirmatory result was known.

```text
(.venv) $ cd <PROJECT_ROOT>
cp <DOWNLOADS>/prereg-v1.2-amendment-A7-sensitivity-operationalization.md docs/
cp <DOWNLOADS>/sensitivity_analysis.py src/
cp <DOWNLOADS>/test_sensitivity_analysis.py tests/
pytest tests/test_sensitivity_analysis.py -q
pytest -q
python -m py_compile src/sensitivity_analysis.py
git diff --check
git status --short
.....                                                                                                                                                                                                   [100%]
5 passed in 0.60s
...............................................................................................................................................................                                         [100%]
159 passed in 21.97s
?? docs/prereg-v1.2-amendment-A7-sensitivity-operationalization.md
?? results/primary_e3_run_83cc8d1/
?? src/sensitivity_analysis.py
?? tests/test_sensitivity_analysis.py
(.venv) $ cd <PROJECT_ROOT>
printf '\nresults/primary_e3_run_83cc8d1/\n' >> .git/info/exclude
git add \
  docs/prereg-v1.2-amendment-A7-sensitivity-operationalization.md \
  src/sensitivity_analysis.py \
  tests/test_sensitivity_analysis.py
git commit -m "freeze post-primary sensitivity analysis plan"
git log -1 --oneline
git status --short
[master c6c9cb4] freeze post-primary sensitivity analysis plan
 3 files changed, 741 insertions(+)
 create mode 100644 docs/prereg-v1.2-amendment-A7-sensitivity-operationalization.md
 create mode 100644 src/sensitivity_analysis.py
 create mode 100644 tests/test_sensitivity_analysis.py
c6c9cb4 (HEAD -> master) freeze post-primary sensitivity analysis plan
```

### 14.2 Interrupted run

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python src/sensitivity_analysis.py
[01/38] sensitivity preprocessing phase1:<participant>
[omitted: progress lines]
^CTraceback (most recent call last):
  File "<PROJECT_ROOT>/src/sensitivity_analysis.py", line 566, in <module>
    main()
    ~~~~^^
  File "<PROJECT_ROOT>/src/sensitivity_analysis.py", line 484, in main
    out_roll.append(rolling_outcome(
                    ~~~~~~~~~~~~~~~^
        stats[arm], onset, info["episode_onsets"],
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        arm, phase, pid, cfg
        ^^^^^^^^^^^^^^^^^^^^
    ))
    ^
  File "<PROJECT_ROOT>/src/sensitivity_analysis.py", line 358, in rolling_outcome
    flags, _ = dynamic_alert_days(
               ~~~~~~~~~~~~~~~~~~^
        res, onset, episode_onsets, 2.0, cfg
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "<PROJECT_ROOT>/src/sensitivity_analysis.py", line 322, in dynamic_alert_days
    P.calibrate_tau(hist, budget, cfg)["tau"]
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "<PROJECT_ROOT>/src/tod_z.py", line 203, in calibrate_tau
    rates = [(float(t), achieved_rate(res_cal, float(t), cfg)) for t in cfg.tau_grid]
                        ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^
  File "<PROJECT_ROOT>/src/tod_z.py", line 188, in achieved_rate
    return float(alert_days(res, tau, cfg).sum()) / (n / DAYS_PER_MONTH)
                 ~~~~~~~~~~^^^^^^^^^^^^^^^
  File "<PROJECT_ROOT>/src/tod_z.py", line 175, in alert_days
    if prev is not None and (r.day - prev).days > cfg.max_gap_days:
                             ^^^^^
  File "<PROJECT_ROOT>/.venv/lib/python3.14/site-packages/pandas/core/generic.py", line 6179, in __getattr__
    @final

KeyboardInterrupt
```

### 14.3 Completed run and consistency check

Estimation only; no p-values.

```text
(.venv) $ cd <PROJECT_ROOT>
source .venv/bin/activate
python src/sensitivity_analysis.py
[01/38] sensitivity preprocessing phase1:<participant>
[omitted: 37 per-participant progress lines]
=== SENSITIVITY SUMMARY — ESTIMATION ONLY, NO P-VALUES ===
                               scenario comparison  N  W  L  T    theta  theta_bca95_lo  theta_bca95_hi
                            phase2_only         H1 25  7 11  7 0.420000        0.260000        0.580000
                            phase2_only         M1 25 11  9  5 0.540000        0.360000        0.720000
                            phase2_only         H2 25  8 10  7 0.460000        0.300000        0.640000
                            phase2_only         H3 25  2  8 15 0.380000        0.260000        0.500000
common_cohort_all_primary_arms_Cfloor16         H1 30  8 12 10 0.433333        0.300000        0.583333
common_cohort_all_primary_arms_Cfloor16         M1 30 13 11  6 0.533333        0.366667        0.683333
common_cohort_all_primary_arms_Cfloor16         H2 30 10 10 10 0.500000        0.350000        0.650000
common_cohort_all_primary_arms_Cfloor16         H3 30  2  9 19 0.383333        0.283333        0.483333
   coarse_calibration_resolution_le_1pm         H1 18  5  7  6 0.444444        0.250000        0.638889
   coarse_calibration_resolution_le_1pm         M1 18  5  9  4 0.388889        0.194444        0.611111
   coarse_calibration_resolution_le_1pm         H2 18  6  6  6 0.500000        0.305556        0.694444
   coarse_calibration_resolution_le_1pm         H3 18  2  5 11 0.416667        0.277778        0.555556
          exclude_multiple_episode_rows         H1 30  8 12 10 0.433333        0.300000        0.583333
          exclude_multiple_episode_rows         M1 30 13 11  6 0.533333        0.366667        0.683333
          exclude_multiple_episode_rows         H2 30 10 10 10 0.500000        0.350000        0.650000
          exclude_multiple_episode_rows         H3 30  2  9 19 0.383333        0.283333        0.483333
                        alert_budget_B1         H1 30  9 10 11 0.483333        0.333333        0.633333
                        alert_budget_B1         M1 30 12  9  9 0.550000        0.400000        0.700000
                        alert_budget_B1         H2 30  9 10 11 0.483333        0.350000        0.633333
                        alert_budget_B1         H3 30  6  5 19 0.516667        0.416667        0.616667
                        alert_budget_B4         H1 30  9 12  9 0.450000        0.300000        0.600000
                        alert_budget_B4         M1 30 14 10  6 0.566667        0.400000        0.716667
                        alert_budget_B4         H2 30 11 11  8 0.500000        0.333333        0.650000
                        alert_budget_B4         H3 30  1  8 21 0.383333        0.283333        0.466667
 todz_without_time_of_day_normalisation         H1 30  9 12  9 0.450000        0.300000        0.600000
 todz_without_time_of_day_normalisation         M1 30 13 10  7 0.550000        0.383333        0.700000
 todz_without_time_of_day_normalisation         H2 30 10 13  7 0.450000        0.300000        0.616667
 todz_without_time_of_day_normalisation         H3 30  3 10 17 0.383333        0.266667        0.500000
              rolling_tau_recalibration         H1 30  6 13 11 0.383333        0.250000        0.533333
              rolling_tau_recalibration         M1 30 12 12  6 0.500000        0.333333        0.666667
              rolling_tau_recalibration         H2 30  8 10 12 0.466667        0.333333        0.600000
              rolling_tau_recalibration         H3 30  2  9 19 0.383333        0.283333        0.483333
             m1_realised_minute_matched         M1 30 13 11  6 0.533333        0.366667        0.700000
Saved: <PROJECT_ROOT>/results/primary_e3_run_83cc8d1/sensitivity_analysis/sensitivity_summary.csv
Confirmatory H1 result remains unchanged and gate remains closed.
(.venv) $ cd <PROJECT_ROOT>
python - <<'PY'
import pandas as pd
from pathlib import Path
p = Path("results/primary_e3_run_83cc8d1/sensitivity_analysis")
s = pd.read_csv(p/"sensitivity_summary.csv")
print("Rows:", len(s))
print("Scenarios:", s["scenario"].nunique())
print("Missing theta:", s["theta"].isna().sum())
print("Theta outside [0,1]:", ((s["theta"] < 0) | (s["theta"] > 1)).sum())
print("N <= 0:", (s["N"] <= 0).sum())
print("W+L+T != N:", ((s["W"]+s["L"]+s["T"]) != s["N"]).sum())
print("Unexpected p-values:", s["sensitivity_p_value"].notna().sum())
print("\nScenario counts:")
print(s.groupby("scenario")["comparison"].count())
PY
Rows: 33
Scenarios: 9
Missing theta: 0
Theta outside [0,1]: 0
N <= 0: 0
W+L+T != N: 0
Unexpected p-values: 0
Scenario counts:
scenario
alert_budget_B1                            4
alert_budget_B4                            4
coarse_calibration_resolution_le_1pm       4
common_cohort_all_primary_arms_Cfloor16    4
exclude_multiple_episode_rows              4
m1_realised_minute_matched                 1
phase2_only                                4
rolling_tau_recalibration                  4
todz_without_time_of_day_normalisation     4
Name: comparison, dtype: int64
```

## 15. Final tables and figures

### 15.1 Tables, figures and the last recorded commit

```text
(.venv) $ cd <PROJECT_ROOT>
cp <DOWNLOADS>/make_final_tables_figures.py src/
python src/make_final_tables_figures.py
PASS — final tables and figures created
Output directory: <PROJECT_ROOT>/results/primary_e3_run_83cc8d1/final_tables_figures
figure_h1_sensitivity.pdf
figure_h1_sensitivity.png
figure_m1_sensitivity.pdf
figure_m1_sensitivity.png
figure_primary_effects.pdf
figure_primary_effects.png
final_results_digest.txt
table_h1_robustness.csv
table_h1_robustness.md
table_primary_confirmatory_results.csv
table_primary_confirmatory_results.md
table_sensitivity_results.csv
table_sensitivity_results.md
(.venv) $ cd <PROJECT_ROOT>
git add src/make_final_tables_figures.py
git commit -m "add final results tables and figures"
git log -1 --oneline
git status --short
[master 9e9b592] add final results tables and figures
 1 file changed, 227 insertions(+)
 create mode 100644 src/make_final_tables_figures.py
9e9b592 (HEAD -> master) add final results tables and figures
```
