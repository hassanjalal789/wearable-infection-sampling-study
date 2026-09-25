# Analysis pipeline, environment and tests

*Publication-stage guide, written on 24 September 2026 for research I designed and conducted. It explains the detector, the threshold calibration, the primary runner and the confirmatory statistics, what the test suite covers, and what I re-ran for this publication. It is new explanatory writing. The code, tests, environment records and audit reports it points to are byte-identical to the versions I preserved during the research process; I have not retrospectively edited them for publication. The chronology validator and its tests are new code, written for this repository and labelled as such.*

## 1. From source minutes to a paired result

For each of the 38 cohort participants, [`src/primary_e3_experiment.py`](../src/primary_e3_experiment.py) reads the heart-rate and step records from the two source archives, builds a minute-level calendar, applies each schedule from [`src/schedules.py`](../src/schedules.py), and scores what each schedule would have seen. Its frozen settings are the CENTRAL E3 budget of seven ten-minute bursts, an alert budget of at most 2 alert-days per person-month, a calibration floor of 16 z-defined days, calibration through onset − 28, and the presymptomatic window onset − 21 to onset − 1. They are set out in [amendment A5](prereg-v1.2-amendment-A5-runner-operationalization.md). Phase-2 step records follow the correction in [amendment A6](prereg-v1.2-amendment-A6-phase2-sparse-step-semantics.md).

**Detector.** [`src/tod_z.py`](../src/tod_z.py) computes one statistic per day from resting minutes only, where rest means a recorded step count of zero:

1. The baseline is the most recent 28 days that each carry at least five resting samples, strictly before the day scored, and no older than 90 calendar days.
2. From those days it estimates an expected resting heart rate for each hour of the day, using only hours with at least seven observations.
3. The day's statistic is its mean deviation from that hourly profile, standardised by the median and scaled median absolute deviation of the same statistic over the baseline days, with a floor of 1 beat per minute on the scale.

The baseline for a day reads only data from before that day. A day with no heart-rate sample is recorded as unevaluable, not as a day without an alert. This is the single-pass baseline of [amendment A3](prereg-v1.2-amendment-A3.md); the [methods guide](METHODS_GUIDE.md#4-corrected-baseline-rule) explains what it replaced.

**Alerts and calibration.** An alert day needs the statistic at or above a threshold τ on two consecutive valid days no more than three calendar days apart. For each participant and schedule, τ is chosen on the calibration days as the smallest value on a grid from 1.0 to 6.0 in steps of 0.1 whose alert rate stays within 2 alert-days per person-month. An infinite threshold, which never alerts, closes the grid, so every participant meets the budget. A schedule with fewer than 16 z-defined calibration days is not calibrated at all.

**Outcomes.** A schedule detects a participant if it raises an alert on a valid day between onset − 21 and onset − 1. Its warning time is the number of days from its first such alert to onset. A non-detection has no warning time; it is never counted as zero. Onset day itself is recorded separately and does not count towards the result.

**Pairs.** Two schedules form an evaluable pair for a participant only if both meet the calibration floor and both have at least one valid day in the window. A detection beats a non-detection, and between two detections the earlier warning wins. Everything else is a tie.

## 2. The confirmatory statistics

The statistics were computed by a separate step after the runner had written its outputs. The script is published in [`evidence/scripts/`](../evidence/scripts/) together with a quality-check script that inspects the corrected run's manifest, table structure, Phase-2 step semantics, calibration and evaluability without reporting any detection result. Both were kept alongside the project rather than inside it.

- **Effect:** θ = (wins + 0.5 × ties) / paired N, over every evaluable pair.
- **Test:** an exact two-sided binomial sign test on wins against losses, at α = 0.05. [`src/verify_test_equivalence.py`](../src/verify_test_equivalence.py) checks, on constructed win-loss-tie counts, that a within-participant sign-flip permutation test on θ gives the same answer.
- **Interval:** a 95% BCa bootstrap over participants, with 10,000 resamples and a recorded seed. The seed affects only the interval, never a testing decision.
- **Gate:** H1 first; M1 only if H1 rejects in favour of nighttime sampling; H2 and H3, with a Holm correction, only if M1 then also rejects in favour of nighttime sampling. H1 did not reject, so the gate closed and every later comparison is estimation-only.

Two versions of the reveal script are preserved. They differ in one line, in the printed summary that follows the writing of the output files, where a column named `T` was read as a table attribute. The computations are the same in both.

## 3. What cannot be re-run from this repository

The runner guards its own evidence. With `--run-real` it refuses to start unless the energy-freeze commit is an ancestor of the current commit, the runner itself is committed, and the working tree is clean, and it writes once into a directory named after the commit, refusing to overwrite. That guard is how the preserved project history shows that the energy parameters were fixed before any outcome existed.

This repository does not contain that history, so the guard fails here by design. I ran `python src/primary_e3_experiment.py --preflight` in a clean copy of this repository on 24 September 2026; it stopped with `Energy freeze commit 4023717 is not an ancestor of HEAD`. I have not added a mode that bypasses the check. A new mode could not recreate evidence that a choice was frozen before the outcomes were known, and the run would also need the two source archives and the withheld cohort and onset-label files.

The reveal and quality-check scripts expect the project in a folder named `rq1` in the user's home directory and read participant-level outputs that are not published, so they cannot run from here either. They are published unchanged as the record of how the statistics were computed.

## 4. The test suite

[`tests/`](../tests/) holds the historical suite. It runs on synthetic data built in [`tests/synth.py`](../tests/synth.py) and on the published configuration and aggregate files; no test reads a source archive. Among other things, the tests check that the detector never reads a future timestamp, that the corrected baseline needs a single 28-day window, that missing days are unevaluable rather than negative, that energy terms are not double-counted and E3 resolves to seven bursts, that M1 matching gives both arms the same count, and that the Phase-2 step correction touches only what A6 allows.

The preserved records report the suite at different points: 131 passing in the environment record [`environment/provenance.txt`](../environment/provenance.txt), 140 at the [pre-outcome checkpoint](PRE_OUTCOME_CHECKPOINT.md), and 159 in the archived report [`evidence/audit/audit_pytest.txt`](../evidence/audit/audit_pytest.txt). Those are historical results.

**Run for this publication, 24 September 2026:**

| Item | Value |
|---|---|
| Command | `python -m pytest tests/ -q`, and `make test`, from the repository root |
| Environment | Fresh virtual environment: Python 3.13.13, NumPy 2.4.4, pandas 3.0.2, SciPy 1.17.1, pytest 9.1.1, Matplotlib 3.10.9, PyArrow 25.0.1, openpyxl 3.1.5, tabulate 0.10.0; Linux x86-64 |
| Result | **161 passed**, 0 failed, 0 skipped |
| Of which historical | 139 tests from the 17 historical test modules published here |
| Of which new | 22 tests for the chronology validator |

The other 20 historical tests belonged to modules published on 25 September 2026: 13 for the power simulation and 7 for the upstream reproduction checks.

**Run again on 25 September 2026,** in the same environment, after those modules were added: **174 passed**, 0 failed, 0 skipped. That is 152 historical tests and the 22 validator tests. The 7 Gate B tests in `tests/test_reproduction.py` read two supplementary workbooks from the source studies, which are not redistributed, so the new root [`conftest.py`](../conftest.py) leaves that module uncollected when the workbooks are absent and names them in the session header. With the two workbooks in `metadata/`, checked first against the checksums in my preserved research record, the suite gave **181 passed**. The [gates guide](REPRODUCTION_GATES_AND_POWER.md#5-what-was-re-run-for-this-publication) describes that run.

Passing tests show that the published code behaves as its tests expect on synthetic inputs, published aggregates and, for Gate B, the source studies' published tables. They do not re-run the analysis on the source data.

## 5. Environment records

[`environment/`](../environment/) keeps the historical records unchanged; [its README](../environment/README.md) describes each file. They are not a tested installation recipe. The main lock file is a full package listing of a general-purpose environment rather than a minimal specification, the three Dockerfiles belong to the upstream reproduction checks, and the records report different Python versions at different points. The environment I actually used for the publication run is the one in the table above.

The [`Makefile`](../Makefile) and the original ignore rules, [`environment/project.gitignore`](../environment/project.gitignore), are also published unchanged. Of the Makefile targets, only `make test` was run for this publication.

## 6. The chronology validator

[`src/validate_chronology.py`](../src/validate_chronology.py) is new code, written for this repository. It checks the machine-readable chronology in [`evidence/timeline_facts.json`](../evidence/timeline_facts.json) against the public documents:

- the required timeline paragraph appears verbatim in the overview and the publication notes;
- dates are unambiguous, and timestamps with an offset are converted to Asia/Karachi rather than guessed;
- every historical, active or completed event cites a readable published source;
- the 28 and 29 September targets stay targets until completion evidence exists, and no document claims otherwise;
- the order of events respects the preserved records;
- the primary analysis is not dated after amendment A7, which records its outcomes as already known;
- the authoritative real-data run is not relabelled as setup output;
- any later analysis carries its own plan, execution evidence and results, and leaves the primary analysis unchanged.

Its tests build synthetic chronologies that are each wrong in one way, and check that each is rejected for that reason alone, plus one genuine later analysis that must pass. On 24 September 2026, `python src/validate_chronology.py` reported **15 events, no unresolved finding**.

The validator checks that claims are supported and consistent. It cannot establish that a cited record is true, date an event more precisely than its source, or certify authorship, research ethics or clinical validity. File times, Git dates and a passing check are not treated as evidence that a historical event happened.
