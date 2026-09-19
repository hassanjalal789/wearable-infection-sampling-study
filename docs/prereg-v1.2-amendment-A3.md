# Preregistration amendment A3 — implementation patches 1–7

**Status: DRAFT — NOT FROZEN.** Issued 31 August 2026. A3 supplements A1 and A2.

---

## A3.1 — Baseline definition, resolved (audit item 7), CORRECTED 1 Sep 2026

**The question.** `tod_z.py` restricted baseline values to the preceding 28 **calendar**
days and then required 28 valid values inside that window — which effectively demanded that
**all 28 preceding calendar days be valid**. prereg-v1.1 §4 says "the trailing 28 valid days".

**Decision: the most recent 28 VALID days, with a 90-calendar-day lookback cap.** Not
"valid days falling inside the trailing 28 calendar days".

**Rationale.**

1. It is what the preregistration already says. "Trailing 28 valid days" reads as the most
   recent 28 valid days; the implementation was stricter than the text.
2. The strict reading is a **direct confound with the exposure**. Requiring 28 consecutive
   valid calendar days is close to unachievable at low duty cycles, so a sparse arm would
   produce far fewer evaluable days than a dense one, and part of any measured difference
   between schedules would be the detector's own validity gate rather than sensing
   placement. That is precisely the artefact this study exists to avoid.
3. **Measured, on synthetic records** <span>`MEASURED`</span>: under the resolved rule a
   sparse arm (one rest sample per night hour) and a dense arm (six) both yield **94
   z-defined days from 150**, identical. A record with 30 % of days missing at source still
   yields 49. Under the calendar-window rule the sparse and gappy cases would have been
   penalised relative to the dense one.
4. The **90-day lookback cap** is new and keeps the baseline physiologically current, since
   resting heart rate drifts with season, fitness and weight. It is set at roughly three
   times the nominal window, consistent with Mishra's 28-day baseline and CovIdentify's
   −60…−22-day baseline. **It is a new free parameter and needs your approval before the
   freeze.**

**One history rule now governs both statistics.** The hour-of-day baseline μ(p,h) is
computed from the same selected 28 valid days as the location and scale.

### Correction, 1 September 2026 — the nested burn-in

Independent reproduction found that the first implementation of this rule did **not**
deliver what the paragraph above promises. On a fully valid 150-day synthetic record it
produced a first D-valid day of 29 but a **first z-defined day of 57**, and 94 z-defined
days of 150 — an effective ~56-valid-day burn-in.

**Cause.** Two 28-day requirements were nested: D became valid only after 28 historical
days, and z only after 28 historical **D values**, each of which carried a baseline of its
own. Besides doubling the burn-in, this let information reach z_d from before the declared
90-calendar-day cap, because those historical D values were computed against still-earlier
baselines. The stated cap was therefore not the true information horizon.

**Corrected implementation — single pass.** For prediction day *d*:

1. `B` := the most recent 28 **baseline-eligible** days strictly before *d* and no older
   than 90 calendar days. Baseline-eligible is a history-free property — the day carries at
   least `min_rest_samples` retained rest samples — so selecting the baseline cannot itself
   depend on an earlier baseline. That independence is what removes the nesting.
2. μ(p,h) is estimated from the retained rest samples on **those** days.
3. One historical `D_j` is computed for each day in `B`, using that **same** μ.
4. Location and scale are the median and MAD of those `D_j`.
5. `D_d` for the current day uses the same μ.
6. `z_d = (D_d − median(D_j)) / max(1.4826 · MAD(D_j), 1 bpm)`

**Verified after the fix** <span>`MEASURED`</span>, same 150-day record: first D-valid day
**29**, first z-defined day **29**, z-defined days **122 / 150**. D-validity and
z-definition now begin on the same day, which is the signature that the nesting is gone.

**Tests added** (`tests/test_baseline_single_pass.py`, 11 tests): the first z-defined day
follows exactly 28 baseline-eligible historical days; no nested gap between D-validity and
z-definition; the baseline never reaches past the 90-day lookback, asserted on both the
oldest baseline day and the minimum timestamp read; **corrupting every sample older than
d − 90 leaves z_d bit-identical**, which is the behavioural proof that the cap is now the
true information horizon; sparse and dense schedules produce identical first-prediction
days, identical z-defined counts and identical baseline sizes; gaps delay the first
prediction by exactly the number of missing valid days; no future timestamp is read;
truncating the future leaves earlier statistics unchanged; and on a constant record a
single shared μ yields exactly zero D_j scatter, so z = 0 — which would not hold if μ were
re-estimated per historical day.

**Feasibility consequence.** The correction is favourable: the usable record per participant
grows by roughly 28 days, so **arm-specific evaluability and z-defined calibration
availability improve relative to the superseded implementation; source-defined base-cohort
eligibility is unchanged.** Base-cohort eligibility rests on `C_p^src`, which is computed
from source availability before any masking and is therefore independent of TOD-z. No
preregistered quantity moves in the unfavourable direction, and the 90-day lookback stands
as declared rather than as an understatement.

**Three distinct notions of a "valid" day, kept apart deliberately.** *Source-valid* — the
archive delivered enough coverage that day (the analysable-day rule, §3.1). *Baseline-
eligible* — the arm's retained stream carries at least `min_rest_samples` rest samples that
day, a history-free property used to select the baseline set. *z-defined* — a z score exists
for that day, which additionally requires 28 baseline-eligible historical days inside the
lookback. Where this document previously said "valid days" in the baseline context it now
says **baseline-eligible historical days**.

**Zero-delivery days are represented, not dropped.** A scheduled participant-day with no
delivered heart-rate sample appears in the detector output as an unevaluable row —
`valid = False`, `z_defined = False`, `D` and `z` NaN, `reason = "source_missing_day"`,
`n_rest_samples = 0` — and is never scored as a non-detection. `daily_statistics()` builds
its calendar skeleton before dropping missing HR and accepts an `expected_days` calendar, so
every scheduled day is represented exactly once in the invalid-day diagnostics.

**The 90-day lookback is a prespecified design choice.** It is not an empirically established
optimum, and neither Mishra et al. nor the CovIdentify work established it. Those studies are
cited only to show that baselines of this order of magnitude are conventional in this
literature.

Prereg §4 wording becomes: *"μ(p,h) and the location/scale are computed over the most recent
28 valid days for that participant and arm, all falling within the preceding 90 calendar
days; a day with fewer than 28 such valid predecessors is not evaluable."*

---

## A3.2 — M1 matching is now exact (audit item 1)

`_max_packing` reports the optimal packing, but the previous `_even_spread` greedy could
strand the remaining budget and return fewer bursts, so `N' = min(max_night, max_day, budget)`
did **not** guarantee that S3ʳ and S6 each received N'. The claim was false as implemented.

**Fixed by Option A.** `_even_spread` is now feasibility-aware: a right-to-left suffix
capacity table `cap[i]` gives the maximum non-overlapping bursts selectable from `starts[i:]`,
and a candidate is admissible only if choosing it still leaves capacity for every remaining
burst. Among admissible candidates it takes the one nearest the ideal evenly-spaced target,
ties to the smaller minute. **Guarantee: exactly N starts whenever N ≤ max packing.**
Deterministic, no seed. `cap[0]` equals `_max_packing` by construction, not coincidence.

**Asserted, not claimed.** `tests/test_m1_matching.py` exercises thousands of synthetic rest
patterns — clustered and scattered — and for every available M1 participant-day asserts:
identical scheduled burst count in both arms, no overlap within either arm, all S3ʳ bursts
rest-only and inside the night window, all S6 bursts rest-only and inside the day window,
identical burst length, identical matched N, and rest purity exactly 1.0 wherever samples
were delivered. A hostile two-cluster pattern designed to strand a naive greedy is included,
as is a check that the suffix table agrees with the greedy optimum over 800 random inputs.

---

## A3.3 — The alert budget is now always satisfied (audit item 2)

The grid is extended by a terminal **τ = +∞**, which produces zero alerts and is therefore
always admissible.

```
tau_p := min { tau in {1.0 .. 6.0} : A(tau) <= B }   if that set is non-empty
         +infinity                                    otherwise
```

Reported per participant: `finite_threshold` and `calibration_saturated`. The previous
behaviour clamped to 6.0, flagged, and retained the participant — which could leave a cell
whose realised calibration alert rate **exceeded** B inside a primary comparison, violating
the equal-alert-budget condition the design rests on. Every participant now stays paired
**and** satisfies the budget. `calibrate_tau` asserts `achieved_rate <= B` before returning.

**The frequency of infinite thresholds is a headline diagnostic**, reported per arm and per
energy level, because an arm that saturates often is one whose z-distribution the budget
cannot tame — itself a finding about that sensing schedule.

---

## A3.4 — Overlap check: dimensional bug fixed (audit item 3)

The previous code compared `night_observed_minutes` — a count of **minutes** — against
`MAD_THRESHOLD_BPM = 1.5`. That is dimensionally invalid and was not an HR comparison.

**Both branches implemented, and the code now matches the claim.**

- With `--hr-series` (columns: phase, participant_id, date, `nightly_median_rhr_bpm`) the
  script performs a real bpm comparison: correlation ≥ 0.95 **and** mean absolute difference
  ≤ 1.5 **bpm**, or ≥ 98 % exact daily agreement, over ≥ 14 common days.
- Without it, **no pseudo-HR comparison is performed**. The verdict is `UNDETERMINABLE`.
  Coverage similarity is computed and reported as `supplementary_coverage_similarity` with
  an explicitly unitless correlation threshold, is labelled `units: minutes`, and **cannot
  decide the verdict**.
- Date plausibility is still checked first; if either archive's dates fall outside its
  published study window, no series comparison of any kind runs.

Prereg §3.4 wording becomes: *"Overlap is investigated using identifiers, date ranges, and —
where both releases carry plausible calendar dates and a per-participant nightly median
resting heart-rate series in bpm can be constructed — a heart-rate identity comparison with
bpm-denominated thresholds. Where that series cannot be constructed, overlap is
undeterminable from the de-identified releases and is reported as such; coverage similarity
may be reported as supplementary evidence but is not an identity test. The Phase-2-only
sensitivity analysis runs regardless of the verdict."*

---

## A3.5 — C_p^src excludes every infection window (audit item 4)

Implemented as specified, and extended in one respect the audit did not name: an
**asymptomatic** episode has no onset date but still contaminates the negative period, so
episode anchors are taken as onset where present and **diagnosis date otherwise**. C_p^src
removes the union of `[anchor_i − 21, anchor_i + 21]` over all episodes, not only the index
one. Unit tests cover a two-episode participant whose earlier asymptomatic episode sits
inside the pre-index history, boundary days at exactly ±21, and idempotence for duplicated
anchors.

---

## A3.6 — Pipeline and preflight (audit item 5)

`run_phase1.sh` now chains inventory → device map (with optional curated external
provenance) → cohort (`--device-map`) → coverage (`--device-map --cohort`) → overlap, and
preserves all outputs and checksums. It **fails loudly** when `device_map.csv` is missing,
when any positive case remains `UNKNOWN` or `CONFLICT`, or when `onset_labels.csv` is absent.
`./run_phase1.sh --preflight` verifies every command, dependency and input file and computes
nothing.

---

## A3.7 — Power simulation replicate count (audit item 6)

`mde_search` previously ran `max(500, reps // 4)` replicates per candidate cell while the
metadata reported the outer `reps`, so a documented 4,000 was an actual 1,000. **The
reduction is removed**: every candidate cell now runs the full requested count, and the
metadata records `reps_requested` and `effective_reps_per_candidate_cell` separately so the
two can be checked against each other. The frozen run uses 4,000.

Dependence remains **swept**, never estimated from S1. A `--sweep-p-b` option sweeps
plausible marginal baseline probabilities instead of taking one from S1, and is the
preferred setting for the frozen run because it uses **no result-derived input at all**. If
`--p-b` is used, the logged record states that it is the only result-derived input and that
no analysis rule is changed on the basis of it.


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
