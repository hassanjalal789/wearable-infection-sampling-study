# Preregistration v1.1 — DRAFT, NOT FROZEN

**Title.** Energy-Matched Heart-Rate Sensing Schedules for Pre-Symptomatic Infection Detection on Low-Cost Wearables

**Supersedes.** prereg-v1 (draft, 31 Aug 2026). Revised 31 Aug 2026 following independent methodological review of the Phase 0 audit.

**Status.** `DRAFT — NOT FROZEN`. This document may **not** receive the git tag `prereg-v1` until every item in §0.2 is resolved. No primary schedule analysis may be run before that tag exists.

| Field | Value |
|---|---|
| Version | v1.1 draft |
| Frozen on | `[NOT YET FROZEN]` |
| Commit at freeze | `[SHA]` |
| Author | `[NAME]` |
| Paper deadline | 10 October 2026 |

---

## 0. Status, scope and freeze conditions

### 0.1 What is already fixed

The design skeleton below — hypotheses, gatekeeping order, detector structure, calibration algorithm, schedule definitions, edge-case rules, energy accounting policy, estimand and test — is fixed as written. Changes to any of it after the freeze tag are deviations and go in the register (§21).

### 0.2 Freeze conditions — all must be satisfied before tagging

1. Actual eligible N, reported as the full participant-flow counts in §3.3.
2. Dataset manifests and SHA-256 checksums for both archives, with download URLs and UTC timestamps.
3. Onset-label availability confirmed for every eligible participant, with the provenance of each date.
4. Absolute E1–E4 values in mJ·day⁻¹ from bench measurement, written to `configs/energy_budgets.json`.
5. Hardware measurement configuration finalised and recorded (§8.4), including which shunt was used for which current range and the measured burden voltage.
6. Final MDE / power / precision figures from `src/power_sim.py` re-run at the audited N (§15).
7. All TOD-z edge-case rules implemented and unit-tested (§6).
8. Calibration algorithm implemented and unit-tested (§5).
9. Final S6 / S3ʳ matching rule implemented and unit-tested (§7.4).

### 0.3 Explicitly out of scope for this study

Adding a quickest-change-detection-optimal acquisition policy as a seventh schedule. It is listed as future work in §18 and may only be attempted if the complete core experiment is finished ahead of schedule, in which case it is reported as an exploratory addition and never enters the confirmatory family.

---

## 1. Terminology commitment

- The exposure is **nocturnally-concentrated sampling**, equivalently **nighttime-window sampling**. The window is a fixed clock interval (00:00–06:59 local), not a physiological sleep interval.
- The term **sleep-window sampling** is **not** used, because participant sleep records do not define the window in the primary analysis.
- The word **circadian** does not appear in the title, abstract, research question, hypotheses, or primary conclusions. It appears only in the Discussion, as one candidate mechanism among sleep-state autonomic tone, reduced behavioural confounding (caffeine, meals, exertion, posture) and improved PPG signal quality — none of which this design adjudicates.
- A positive M1 licenses exactly one claim: *"a time-of-day advantage that persists after rest-state matching."*
- An exploratory sensitivity may define a participant-specific window from Phase 1 sleep records, where present, and would be reported as **sleep-record-defined window (exploratory)**. Phase 2's data-availability statement lists heart rate and steps only, so this cannot be a primary or cross-cohort analysis.

---

## 2. Confirmatory structure

### 2.1 Hypotheses

All stated at the primary energy level **E3**, primary detector **TOD-z**, alert budget **≤ 2 alert-days per person-month**, on the primary-analysis cohort.

| ID | Comparison | Role |
|---|---|---|
| **H1** | S3 nocturnally-concentrated vs S2 uniform duty-cycle | Confirmatory, stage 1 |
| **M1** | S3ʳ nocturnal rest-only vs S6 daytime-rest control | Confirmatory, stage 2 (gated) |
| **H2** | S3 vs S5 random-block | Confirmatory, stage 3 (gated) |
| **H3** | S3 vs S4 rest-triggered | Confirmatory, stage 3 (gated) |

M1 is **not** an afterthought. The research question asks whether a nocturnal advantage survives rest-state matching, so M1 carries the interpretive weight of the paper and is inside the confirmatory sequence.

### 2.2 Gatekeeping and family-wise error control

A **serial (fixed-sequence) gatekeeping procedure**, which controls the family-wise error rate strongly at α = 0.05 without any alpha adjustment between stages, because each stage is tested only if all preceding stages rejected.

```
STAGE 1   H1 at alpha = 0.05, two-sided.
          Gate opens only if H1 is rejected AND theta_hat(S3,S2) > 0.5,
          i.e. the rejection is in the nocturnally-favouring direction.
          If the gate does not open -> STOP the confirmatory sequence.

STAGE 2   M1 at alpha = 0.05, two-sided.
          Gate opens only if M1 is rejected AND theta_hat(S3r,S6) > 0.5.
          If the gate does not open -> STOP the confirmatory sequence.

STAGE 3   H2 and H3, Holm-Bonferroni across the two, family alpha = 0.05.
```

If a gate does not open, every downstream hypothesis is still **estimated and reported** — point estimate, 95 % CI, discordant counts — but is explicitly labelled **non-confirmatory** and carries no p-value in the abstract or conclusions.

Rationale for ordering M1 second rather than last: a nocturnal advantage that vanishes under rest-state matching would change the interpretation of H2 and H3 entirely, so testing it before the remaining comparators keeps the inferential narrative coherent.

### 2.3 Estimation-only cells

Every other combination — other energy levels (E1, E2, E4), other detectors, all ablations, the sleep-record-defined window sensitivity — is reported as a point estimate with a 95 % CI and **no p-value**. This is stated in Methods so the absence of p-values reads as design rather than omission.

---

## 3. Cohort

### 3.1 Criteria, applied in order

1. Source: Stanford Phase 1 (Mishra et al. 2020) and Phase 2 (Alavi et al. 2022) public archives.
2. **Device: Fitbit only.** Apple Watch and Garmin excluded — the Apple Watch stream in these archives is event-driven and irregular, and a schedule-masking experiment requires a fully observed reference stream. Minutes never sampled by the device cannot be masked, and cannot be retained.
3. Infection-positive under each paper's own confirmation rule.
4. Symptomatic, with a symptom-onset date present. Asymptomatic infections cannot contribute to a symptom-onset endpoint.
5. ≥ 21 of the 28 days before (onset − 1) analysable.
6. ≥ 14 analysable days with `z` defined in the calibration interval (§5.b).

**Analysable day** := ≥ 2 h of observed minutes in 00:00–06:59 **and** ≥ 2 h of observed minutes in 07:00–23:59. The symmetry is deliberate: it is the only way the nocturnal and daytime arms face the same data-availability constraint.

### 3.2 Sample size

**The planning range of 45–60 from the Phase 0 audit is NOT a preregistered value and is not treated as fact.** The cohort is determined entirely by applying §3.1 to the actual archives. `[ELIGIBLE N TO BE FILLED FROM THE ELIGIBILITY AUDIT]`

### 3.3 Counts to record before freezing

Recorded separately for Phase 1 and Phase 2, each as an integer with the filter that produced it:

| Step | Phase 1 | Phase 2 |
|---|---|---|
| Fitbit COVID-positive | `[ ]` | `[ ]` |
| … of which symptomatic | `[ ]` | `[ ]` |
| … with symptom-onset date available | `[ ]` | `[ ]` |
| … with sufficient baseline (criterion 5) | `[ ]` | `[ ]` |
| … with sufficient coverage (criterion 6) | `[ ]` | `[ ]` |
| **Primary-analysis cohort** | `[ ]` | `[ ]` |

### 3.4 Phase 1 / Phase 2 overlap

Neither paper documents participant overlap. Alavi et al. state participants were invited partly through "outreach to participants in previous studies" but quantify nothing, and the two archives use different ID formats. Overlap will be investigated by comparing ID spaces, date ranges and heart-rate series (`src/check_overlap.py`).

**If overlap cannot be determined, this is stated explicitly in Methods and Limitations, the cohort is treated as a stratification variable, and the Phase-2-only sensitivity analysis (§16.4) is retained regardless of the outcome.**

---

## 4. Primary detector — TOD-z

Causal time-of-day-normalised rest-heart-rate z-score.

**All detector structure and calibration rules are fixed a priori; the alert threshold is causally calibrated using historical negative data.** No structural parameter is selected by looking at outcomes.

| Element | Definition | Origin of the fixed value |
|---|---|---|
| rest minute | recorded step count == 0 | Alavi et al. 2022 RHR definition |
| hour-of-day baseline | μ(p, h) = mean rest-HR for participant p, hour h, over the trailing 28 days, computed **from that schedule's own retained samples only** | 28-day window from Mishra et al. 2020 |
| residual | r(t) = HR(t) − μ(p, hour(t)) | — |
| daily statistic | D_d = mean of r(t) over retained rest samples on day d | — |
| valid day | ≥ 5 retained rest samples after all exclusions | declared choice, stated as such |
| scale | s_d = max(1.4826 × MAD₂₈, 1.0 bpm) | floor justified in §6.1 |
| z | z_d = (D_d − median₂₈) / s_d | — |
| alert rule | z_d ≥ τ_p on 2 consecutive valid days | persistence rule of 2 from the NightSignal FSM |
| threshold | τ_p — see §5 | causally calibrated |

**Leakage rule.** The hour-of-day baseline must be estimated from the schedule's own retained samples. Estimating it once on the fully observed stream and reusing it across arms would leak full-resolution information into the sparse arms and would systematically flatter the sparsest schedules.

**Consecutiveness.** "Consecutive valid days" means consecutive in the sequence of valid days, **and** separated by no more than 3 calendar days. A gap of more than 3 calendar days between valid days resets the persistence counter to zero.

---

## 5. Threshold calibration

τ_p is estimated **separately for every (participant × schedule × energy level × detector)** cell. This is required, not optional: equalising the alert budget across arms is what makes the comparison energy-and-alert-matched, and the z-distribution differs by arm.

**a. Historical calibration interval C_p.** Take the participant's analysable days on which `z` is defined and which lie outside every infection exclusion window (§6.10), in **chronological order, earliest first**, accumulating until either 28 such days are collected or the day (onset_p − 28) is reached, whichever comes first.

*On the use of the onset date.* The onset date enters only as a hard causal stop, never as a selection criterion for which negative days are informative. The selection rule is "earliest first" and contains no outcome information. A deployed device would not know a future onset date; our use of it can only shorten the calibration interval, never enrich it. This is stated in Limitations.

**b. Minimum historical negative data.** |C_p| ≥ 14 days with `z` defined. Participants below this fail eligibility criterion 6 and are excluded before any analysis.

**c. Candidate threshold grid.** τ ∈ {1.0, 1.1, 1.2, …, 6.0}, 51 values, fixed. No numerical search, no continuous optimisation — a frozen grid removes any residual investigator freedom.

**d. Achieved alert rate.** A(τ) = (number of alert-days generated over C_p by the **full** alert rule of §4, including the 2-consecutive-valid-day persistence requirement) ÷ (|C_p| / 30.44), in alert-days per person-month.

**e. Selection when several thresholds satisfy the budget.** A(τ) is **monotone non-increasing in τ**: raising the threshold can only remove alert-days, never create them, so {τ : A(τ) ≤ B} is an upper set. Set

```
tau_p = min { tau in grid : A(tau) <= B }
```

i.e. the **smallest** admissible threshold — the most sensitive detector that still respects the budget. Deterministic; no tie-breaking required.

**f. When no threshold achieves the target.** The rule in (e) does not require exactness, only A(τ) ≤ B. If even A(6.0) > B, set τ_p = 6.0, flag the participant **budget-infeasible**, retain them in the primary analysis, and report the count per arm. A prespecified sensitivity analysis excludes budget-infeasible participants (§16.8).

**g. When historical data are insufficient.** Covered by (b): the participant is excluded at the cohort stage, never mid-analysis.

**h. Recalculation over time.** τ_p is **frozen after initial calibration** on C_p and held fixed throughout the evaluation window. Rationale: it is unambiguously causal; it makes the realised alert budget interpretable as a single operating point; and re-estimating inside the evaluation window would draw on data adjacent to the outcome. A prespecified sensitivity uses **rolling re-calibration** on an expanding negative history up to day d−1 (§16.9).

### 5.1 Why within-participant causal calibration is not leakage

Leakage is the use of information that would be unavailable at prediction time, or the use of outcome information to make the predictor look better. Neither occurs here:

- Only data strictly before the evaluation window are used.
- No data from inside any infection window are used.
- No future data are used.
- The infection **label** and the **outcome** (whether or how early an alert precedes onset) play no part in choosing τ. τ is chosen to hit a **negative-period alert rate**, which is a property of the participant's healthy baseline.
- The selection algorithm is frozen before analysis and is byte-identical across schedules, energy levels and detectors.

Participant cross-fitting is therefore **not** introduced. Cross-fitting would be required if τ were tuned against outcomes, which it is not; adding it here would cost participants from a small cohort and buy no protection. This reasoning is stated in Methods so a reviewer can check it rather than infer it.

---

## 6. TOD-z edge cases

Every rule below is fixed now so that no implementation decision affecting results can be invented later. Each has a unit test in `tests/test_edge_cases.py`.

| # | Condition | Rule |
|---|---|---|
| 6.1 | MAD₂₈ = 0 | Apply a scale floor: s_d = max(1.4826 × MAD₂₈, **1.0 bpm**). Heart rate is integer-valued in these archives, so a dispersion estimate below 1 bpm is not physically meaningful. Prevents division by zero and unbounded z. |
| 6.2 | Fewer than 28 trailing valid days | `z` undefined; day is **not evaluable**; no alert can be raised. Counted as `baseline_insufficient`. Not scored as a non-detection. |
| 6.3 | Fewer than 7 observations for hour-of-day h in the trailing 28 days | μ(p,h) is unstable; **all samples falling in hour h on day d are dropped** before computing D_d. If this leaves < 5 rest samples, the day is invalid (6.6). |
| 6.4 | First 28 days of a participant record | Burn-in. `z` undefined, never evaluable, never counted as a miss. |
| 6.5 | Zero retained rest samples on day d | Day invalid. Counted as `invalid_no_rest`. |
| 6.6 | 1–4 retained rest samples on day d | Day invalid. Counted as `invalid_too_few`. Reported per arm; the count is itself a result. |
| 6.7 | Missing step record for a minute | Minute is **not** rest (conservative). Excluded from rest samples. |
| 6.8 | Missing HR for a scheduled minute | No sample delivered. **Energy is still charged** (§8.3). Counted as `source_missing`. |
| 6.9 | Multiple infection episodes for one participant | The **earliest episode with a valid onset date** is the index episode. All other episodes contribute exclusion windows only. Participants with > 1 episode are flagged; §16.10 excludes them as a sensitivity. |
| 6.10 | Overlapping infection exclusion windows | The **union** of all [onset − 21, onset + 21] windows is excluded from negative periods and from calibration. |
| 6.11 | Unknown timezone | Timestamps are interpreted as local wall-clock as recorded. Recorded as an **assumption** in Limitations. No timezone correction is attempted and no participant is excluded on this basis. |
| 6.12 | DST-transition day | Excluded from all analyses. Counted and reported. |
| 6.13 | Insufficient negative calibration history | Excluded at the cohort stage by §5.b / criterion 6. Never handled mid-analysis. |
| 6.14 | Alert raised outside [onset − 21, onset] | Does not count as a detection for the endpoint. Counts toward alert burden only if it falls in a negative period. |

---

## 7. Schedules

### 7.1 Global conventions

- Night window: 00:00–06:59 local, **420 minutes**. Matches the NightSignal implementation exactly.
- Day window: 07:00–23:59 local, **1020 minutes**.
- Burst length **L = 10 minutes** for every schedule. Chosen so that RHR-Diff, whose `rollmean(k=10)` is NA-propagating, remains structurally definable on block-structured arms.
- Rest condition: recorded step count == 0.
- Global seed **20261010**. Per-participant-day seed = `SHA256(global_seed ‖ participant_id ‖ ISO-date)`, so any day is independently regenerable without storing masks.
- **Bursts may never overlap.** Overlap is prevented by construction in S2, S3, S3ʳ, S6 (fixed stride or earliest-eligible scan with enforced spacing) and by rejection sampling in S5.
- **Unspent energy is permitted** but never carried to another day. Every participant-day records `energy_target`, `energy_spent`, `bursts_scheduled`, `bursts_delivered`, `samples_scheduled`, `samples_delivered`.

### 7.2 Burst budget

For a given energy level, the affordable burst count is

```
N = max integer such that  N * (E_wake + E_settle + L*60*P_PPG) + E_act(S) + E_BLE  <=  E_target
```

Because S2, S3, S3ʳ, S5 and S6 share the same L and the same per-burst overhead, **at equal energy they receive the identical N** whenever their E_act terms are equal (see §8.2). Placement is then the only difference between them, which is precisely the experimental contrast.

**S4 may have a different realised N**, for two reasons that are both scientifically meaningful and must be reported rather than corrected away: it pays a larger E_act (§8.2), and its trigger may be scarce (§7.3). S4's realised N is reported alongside every S4 result.

### 7.3 Maximum burst counts and scarcity

| Schedule | Placement domain | Max non-overlapping bursts | Behaviour when the budget cannot be spent |
|---|---|---|---|
| S1 continuous | all observed minutes | n/a | n/a — reference arm, not energy-matched |
| S2 uniform | 1440 min | 144 | N ≤ 144 always reachable within E1–E4 |
| S3 nocturnal | 420 min | **42** | If N > 42 the schedule saturates: retain all 420 night minutes, record unspent energy. Does not occur within E1–E4 by construction (§8.5) |
| S3ʳ nocturnal rest-only | night minutes with steps == 0 | participant-day dependent | Matched down per §7.4 |
| S4 rest-triggered | minutes where steps == 0 has held ≥ 5 consecutive minutes, with a 30-min skip after each burst | participant-day dependent | Use all available qualifying starts; record unspent energy and realised N |
| S5 random-block | 1440 min | 144 | Rejection sampling on overlap; if 1000 rejections occur, fall back to the earliest non-overlapping placement and record the event |
| S6 daytime-rest | day minutes with steps == 0 | participant-day dependent | Matched down per §7.4. **No top-up.** |

### 7.4 S6 is a strict rest-only control, and M1 is rest-matched by construction

**The active-minute top-up rule from prereg-v1 is deleted.** S6 may never fill missing daytime-rest samples with active daytime minutes. Rest purity for S6 is 100 % by definition.

To give M1 a matched counterpart with the same property, the mechanism comparison uses **S3ʳ**, the rest-only instantiation of the nocturnal schedule: identical to S3 except that bursts may start only at night minutes satisfying the same rest condition as S6. S3ʳ is **not** a new arm in the H1/H2/H3 family; it exists solely so that M1 compares like with like.

M1 matching rule, applied per participant-day:

```
N3 = feasible non-overlapping rest-only bursts in the night window
N6 = feasible non-overlapping rest-only bursts in the day window
N' = min(N3, N6, N_budget)

if N' >= N_MIN and both arms yield >= 5 retained rest samples:
        both S3r and S6 are run at exactly N' bursts
else:
        the participant-day is UNAVAILABLE for M1 and is excluded
        from M1 only (it remains available to H1/H2/H3)

N_MIN = 2 bursts
```

Reported for M1, per participant and in aggregate:

- matched sample count N' and the resulting retained-sample counts per arm;
- realised rest purity per arm (expected to be 1.00 by construction — any deviation is a bug and is reported);
- participant-days excluded from M1, with the reason (`N3 < N_MIN`, `N6 < N_MIN`, `too_few_rest_samples`);
- night-window and day-window source coverage for those participant-days, so a reader can see whether exclusions are coverage-driven.

If more than 40 % of participant-days are unavailable for M1, M1 is reported as **inconclusive by construction** and the mechanism question is stated as unresolved. That threshold is fixed here, before any data are seen.

### 7.5 Scheduled versus delivered samples

- **Scheduled** = minutes the schedule selected.
- **Delivered** = scheduled minutes that contain an observed source sample.
- Type A missingness (already in the archive) and Type B missingness (introduced by the schedule) are reported separately for every arm.
- Energy is charged for **scheduled** bursts in the primary analysis (§8.3); delivered-burst charging is a sensitivity (§16.3).

---

## 8. Energy model

### 8.1 The matched quantity

```
E_sched(S) = E_total(S) - E_platform_idle
           = N_bursts * (E_wake + E_settle)
           + T_active  * P_PPG
           + E_act(S)                      <- schedule-dependent, see 8.2
           + N_tx * E_BLE                  <- constant, N_tx = 1 per day
```

Schedules are matched on **E_sched** to ±5 % of the target mJ·day⁻¹.

**E_total** and predicted battery-days on a 1000 mAh cell are reported separately and prominently, for both the NodeMCU-32S board and a bare-module configuration. Methods states plainly that a NodeMCU-32S development board is not a production wearable: its power LED, AMS1117 regulator and USB-UART bridge dominate the platform term and would not appear in a fabricated device. Platform overhead is **measured and reported**, but it is not permitted to swamp the schedule comparison, which is exactly why the matched quantity excludes it.

### 8.2 Activity-sensing energy — option B, chosen on physical grounds

**Decision: option B. Only schedules that require activity information at times when the PPG is off pay the continuous accelerometer cost.**

The reasoning is physical, not convenient. Every arm's detector needs a rest classification for the minutes it actually samples, so every arm runs the accelerometer during its bursts. But three arms additionally need to know the rest state at minutes when the PPG is **off**, in order to decide where to place a burst at all:

| Schedule | Placement rule needs rest state when PPG is off? | E_act(S) |
|---|---|---|
| S1, S2, S3, S5 | No — placement is clock-driven | accelerometer co-scheduled with PPG: `N_bursts × L × 60 × P_accel_active` |
| S3ʳ, S4, S6 | **Yes** — placement is rest-conditional | continuous low-power accelerometer plus MCU trigger evaluations: `86400 × P_accel_lp + N_eval × E_mcu_eval` |

Consequences, all of which are reported rather than hidden:

- H1 (S3 vs S2) compares two clock-driven arms; E_act is equal and cancels.
- M1 (S3ʳ vs S6) compares two rest-conditional arms; E_act is equal and cancels.
- H3 (S3 vs S4) compares a clock-driven arm with a rest-conditional one, so S4 buys fewer PPG bursts at the same total E_sched. **This is the intended accounting.** The research question explicitly requires the rest-triggered schedule to carry the cost of whatever determines that the participant is at rest.

A prespecified sensitivity (§16.5) re-runs everything under **option A**, in which the accelerometer is continuously enabled for all arms so E_act is a common constant — the accounting a product would use if it already ran continuous step counting for other reasons. Reporting both demonstrates the conclusions are not an artefact of the accounting choice.

### 8.3 Charging policy

Energy is charged for every **scheduled** burst, whether or not source data exist at that minute. A real device spends wake and settle energy regardless of whether the resulting reading is usable or the device is being worn. Charging only for delivered bursts would reward a schedule for targeting hours when people do not wear their watch.

### 8.4 Measurement arrangements

Published datasheet and community values are **context only**. Every term is measured on the **actual NodeMCU-32S board** used in the study. A published value may substitute for a measurement only where a measurement failure is explicitly documented in `hardware/measurement_log.md`, naming the term, the instrument, the failure mode and the substituted source.

Two distinct measurement paths, because no single shunt spans the required 15,000:1 dynamic range:

| Path | Target range | Arrangement | Burden voltage | Resolution |
|---|---|---|---|---|
| **Active / wake / PPG / BLE** | ~1 mA – 200 mA | INA219, **0.1 Ω** shunt, PGA set to the narrowest range that does not saturate the observed peak, 9-bit / 84 µs conversions to resolve transients | 15 mV at 150 mA | 100 µA per LSB; ±1 mA equivalent input-offset error — acceptable at these currents |
| **Sleep / platform idle** | ~10 µA – 10 mA | **Separate run**, firmware built with wake disabled so the device never leaves deep sleep, **10 Ω** shunt, long INA219 averaging (64–128 samples) | 47 mV at 4.7 mA | 1 µA per LSB; ±10 µA equivalent offset — 0.2 % at board-level sleep currents |

Rules that go with this:

- The sleep run **must** use a non-waking firmware build. At 10 Ω a 150 mA wake transient would drop 1.5 V across the shunt and brown out the board; any observed reset invalidates the run.
- A µA-range multimeter in series is taken as an independent cross-check on the sleep figure. Disagreement beyond 10 % is recorded and both values reported.
- All measurements are taken at the **3.3 V rail downstream of the regulator**, not at the 5 V USB input, and the paper states which. The same class of board has been reported at 8.84 µA and 1.21 mA depending on probe placement.
- ≥ 30 repetitions per term. Report mean, SD, 95 % CI, instrument resolution, shunt value and PGA setting.
- Model validated by predicting two schedules excluded from the fit, to within 10 %.

### 8.5 The energy ladder

As a fraction of E_sched(S1): **E1 = 0.20, E2 = 0.10, E3 = 0.05 (PRIMARY), E4 = 0.02.**

The ladder sits below 0.29 because the night window holds only 420 of 1440 minutes, so S3 cannot exceed 29.2 % active time. The 100 % and 50 % duty cycles of the original proposal are physically unreachable for the nocturnal arm.

Absolute values: `[FILL FROM BENCH]` → `configs/energy_budgets.json`, written before any masking runs.

**E_settle is the project's single most important unmeasured constant**, and the definition of "first valid PPG sample" must be written down and committed **before** the measurement is taken. If (E_wake + E_settle) turns out small relative to the marginal per-sample cost, the burst-clustering advantage is immaterial and all arms receive near-identical sample counts at equal energy. That does not weaken the research question — it sharpens it, because the comparison then isolates placement at literally equal sample counts. Either outcome is reported as a hardware finding.

---

## 9. Primary endpoint

Pre-symptomatic warning obtained at the fixed alert budget. Warning = (onset date − first alert date) in whole days, counted only for alerts falling in [onset − 21, onset]. A participant with no qualifying alert is a **non-detection**, handled by the hierarchical comparison in §11 rather than by imputing a numeric warning of zero.

---

## 10. Alert budget

### 10.1 Operating point

**Primary: ≤ 2 alert-days per person-month.** Sensitivity: **1** and **4**.

- **alert-day** := a calendar day on which the detector raises an alert for that participant.
- **person-month** := 30.44 valid days of that participant's negative period.
- **negative period** := all analysable days outside the union of every [onset − 21, onset + 21] window.

### 10.2 Justification — corrected

Alavi et al. 2022 report, **in the abstract, verbatim**: alerts triggered by other respiratory infections and by non-infectious events such as stress, alcohol consumption and travel occurred *"at a much lower mean frequency (1.15 alert days per person compared to 3.42 alert days per person for coronavirus disease 2019 cases)"*.

Separately, in Results: *"An individual who tested positive for COVID-19 receives 3.42 alerts on average during the infection detection window, whereas this number is 1.30 for individuals who tested negative for COVID-19 and 1.09 for the remainder."*

The **1.15 figure is real and correctly attributed.** The Phase 0 audit's claim that it could not be sourced was wrong and is retracted.

What remains genuinely uncertain is the **denominator**, and we do not paper over it:

- The abstract's 1.15 is expressed as *alert days per person*; the Results figures of 1.30 and 1.09 are expressed as *alerts* over a stated 21-day infection detection window. The paper uses 3.42 for both the abstract's "alert days per person" and the Results' "alerts … during the infection detection window", which suggests the two phrasings refer to the same quantity — but the paper does not say so, and 1.15 does not equal either 1.30 or 1.09.
- **These statistics are therefore not assumed to share identical denominators or definitions.** If the 21-day window does apply to 1.15, it rescales to ≈ 1.67 alert-days per 30.44-day month; that rescaling is an **inference we make**, labelled as such, not a value read from the paper.

Accordingly: **≤ 2 alert-days per person-month is our prespecified operating point, informed by the operating range reported by Alavi et al., rather than a value copied from a single published statistic.** The sensitivity analyses at 1 and 4 span the range of plausible readings.

A further quantity, 12,186 red alert-days ÷ 99,310 total daily alerts ≈ 12.3 % of person-days, appears in the specificity calculation. **It is not used to justify the operating point and is not presented as equivalent to the participant-level statistics**, because its denominator is all daily alerts issued to non-COVID participants across the whole study rather than a per-person window. It is mentioned once, in a footnote, solely to record that the paper contains alert-frequency statistics on more than one denominator.

---

## 11. Estimand, test and intervals

### 11.1 Estimand

The comparison is a **hierarchical composite** in the sense of the matched-pairs win ratio (Pocock SJ, Ariti CA, Collier TJ, Wang D. *The win ratio: a new approach to the analysis of composite endpoints in clinical trials based on clinical priorities.* Eur Heart J 2012;33(2):176–182, doi:10.1093/eurheartj/ehr352). For each participant, comparing schedule A with schedule B:

```
A WINS   if A detects pre-symptomatically and B does not,
         or if both detect and A's warning is strictly longer
A LOSES  under the reverse
TIE      otherwise (neither detects, or both detect with equal warning)
```

Primary effect estimate, the **win proportion**:

```
theta = (W + 0.5*T) / n
```

**Exact interpretation, to be used verbatim in the paper:** *the probability that a randomly selected paired participant favours schedule A over schedule B, with ties split equally.* It is **not** "in θ of participants A warned earlier" — that reading ignores the half-weighting of ties and is not used.

The **win ratio** W/L is reported alongside, with the discordant counts W and L given explicitly so any reader can recompute either quantity.

### 11.2 Test — the exact sign test, on correctness grounds

Under the randomisation null that the schedule label is exchangeable within participant, a sign-flip permutation maps wins to losses and leaves ties fixed. The permutation distribution of θ is therefore determined entirely by W conditional on the discordant count W + L, which is exactly Binomial(W + L, ½).

**The sign-flip permutation test on θ is not an approximation to the exact binomial sign test — it is the same test.** This was verified numerically (`src/verify_test_equivalence.py`, 200,000 permutations per cell); across seven configurations the two p-values agreed to within 3.8 × 10⁻⁴, i.e. Monte Carlo error.

Preferring correctness and transparency over novelty, the **primary inference is the exact binomial sign test** on (W, L), two-sided, α = 0.05. No permutation machinery is required and none is used for the primary test.

### 11.3 Intervals

- θ: BCa bootstrap over participants, 10,000 resamples.
- Conditional win probability W/(W + L): exact Clopper–Pearson interval.
- Paired difference in warning days (detected-under-both subgroup): BCa bootstrap.
- Paired difference in detection proportion: BCa bootstrap, with McNemar discordant counts reported.

### 11.4 Mandatory reporting set — every comparison, without exception

1. Detection proportion under each schedule.
2. Discordant counts W, L, and the tie count T.
3. Warning times: median with non-detection excluded, median among detected, and the full distribution as a figure.
4. Paired effect estimate: θ, and the win ratio W/L.
5. 95 % confidence interval for every estimate reported.
6. Realised alert burden per arm, in alert-days per person-month, confirming the budget was actually met.
7. Number of invalid days per arm, broken down by reason (§6).
8. **Participant N contributing to that specific analysis**, which differs between H1/H2/H3 and M1 because of the M1 availability rule (§7.4).

---

## 12. Multiplicity

Specified in full in §2.2. In summary: serial fixed-sequence gatekeeping H1 → M1 → {H2, H3 with Holm, m = 2}, strong FWER control at 0.05, no alpha adjustment between stages, gates directional. Everything outside that sequence is estimation only.

---

## 13. Practical equivalence

**No formal equivalence test is preregistered.** The θ ∈ [0.40, 0.60] band from prereg-v1 had no substantive justification and is demoted.

If all confirmatory intervals are narrow and centred near θ = 0.5, the result is described as *"no evidence of a materially different pre-symptomatic warning between schedules at this energy budget, with the observed interval spanning [ … ]"*, and the interval is reported in full. The band [0.40, 0.60] may be quoted as an **exploratory, pragmatic reference range** with that label attached, never as an equivalence margin.

A formal equivalence claim requires precision sufficient to exclude a prespecified margin. Whether this study has such precision is unknown until §15 is filled. If the audited MDE shows it does, a formal margin may be added **before** the freeze tag, with its substantive justification written down at the same time; it may not be added afterwards.

---

## 14. Missingness

- Type A (source) and Type B (schedule) reported separately for every arm.
- **Mandatory pre-experiment diagnostic:** per-participant paired night-versus-day observed-minute fraction, with a bootstrap CI, computed and reported **before** any masking. Fitbit devices are commonly charged overnight, so night coverage may be systematically worse than day coverage; the bias could run in either direction and must be measured, not assumed.
- If night and day coverage differ materially, every S3ʳ–S6 comparison is additionally conditioned on realised sample count, and the limitation is stated in the abstract.
- **No imputation anywhere in our pipeline.** NightSignal's internal single-night imputation is declared as belonging to the published algorithm, not to us, wherever NightSignal results are reported.

---

## 15. Power, MDE and precision

```
Power / MDE / expected CI width = [TO BE FILLED AFTER THE ELIGIBILITY AUDIT]
```

No power or MDE statement is frozen in this version. The Phase 0 figures ("80 % power for +20 percentage points and +2 days") were **planning calculations on an assumption now known to be wrong** and are withdrawn.

### 15.1 What is committed now

`src/power_sim.py`, committed with this document, together with:

| Item | Value |
|---|---|
| RNG seed | 20261010 (same as the schedule seed) |
| Monte Carlo runs | 4,000 per cell |
| Test implementation | exact binomial sign test on the hierarchical win/loss (§11.2) |
| Assumed baseline detection probability | from the **realised S1 reference arm**, not assumed a priori |
| Dependence between paired schedule outcomes | **explicitly modelled** — see 15.2 |
| Warning-time distribution | shared participant effect + schedule-specific noise, rounded to whole days, truncated at 0 |
| Script checksum | recorded in `power_sim_output.json` at each run |

### 15.2 The independence assumption is withdrawn

The Phase 0 simulation drew detection outcomes under the two schedules as **independent** Bernoulli variables. That is not realistic for a within-participant paired experiment: the same person's physiology, wear behaviour and data coverage drive both arms, so detection outcomes and warning times are positively correlated.

The committed simulation models this explicitly. A participant-level latent effect `u_p` shifts the detection probit under both schedules by `λ·u_p`, and a shared participant effect `v_p` shifts warning time under both arms, giving a lead-time correlation of `τ²/(τ² + σ²)`.

The direction of the correction matters and is stated honestly: in illustrative, non-binding runs, positive within-participant correlation **increases** power relative to the independent case, because correlated warning times reduce the variance of the paired difference and make the sign of that difference more reliably reflect the schedule effect — even though correlated detection produces more tied pairs. **The Phase 0 numbers were therefore pessimistic, not optimistic.** No conclusion is drawn from that until the audited N is available.

### 15.3 Before the freeze tag

`src/power_sim.py` is re-run at the audited N, with `λ`, `τ` and `σ` set from the realised S1-arm data, and the resulting MDE and expected CI widths are pasted into this section. The study is reported as an **estimation study**: MDE and interval widths are stated in the abstract, and the phrase "adequately powered" is not used.

---

## 16. Sensitivity analyses

1. Alert budget at 1 and 4 alert-days per person-month.
2. Discrete-time survival with administrative censoring, time running backwards from onset, stratified by participant.
3. Energy charged for **delivered** rather than scheduled bursts.
4. **Phase-2-only cohort** — retained regardless of what the overlap investigation concludes.
5. **Option A energy accounting** — accelerometer continuously enabled for all arms, E_act a common constant (§8.2).
6. TOD-z without the time-of-day normalisation, isolating how much work that step does.
7. Detection-proportion-only endpoint, if the lead-time N triggers §17.
8. Excluding budget-infeasible participants (§5.f).
9. Rolling re-calibration of τ_p on an expanding negative history (§5.h).
10. Excluding participants with more than one infection episode (§6.9).
11. Sleep-record-defined nocturnal window, Phase 1 only, exploratory (§1).
12. Synthetic sensor-degradation ablation, carrying the former RQ2 content.

---

## 17. Stopping and gate rules

If the eligible N is below 15, the primary endpoint switches to **pre-symptomatic detection proportion at the fixed budget** and warning time becomes descriptive. This switch is prespecified here and **may not be made after seeing any schedule comparison**. The switch is triggered by the participant-flow counts alone.

If more than 40 % of participant-days are unavailable for M1, M1 is reported as inconclusive by construction (§7.4).

---

## 18. Reproduction gate and related-work positioning

### 18.1 Reproduction

- **Gate A (required).** Upstream code, run unmodified on the sample participants shipped in its own repository, reproduces that repository's committed output files exactly.
- **Gate B (target).** Our pipeline reproduces published cohort numbers within tolerance. Mishra: 32 analysed cases exact; 26 detected ± 2; median 4 d before onset ± 1 d; 22/25 at or before onset ± 2. Alavi: 84 confirmed positives exact; sensitivity 80 % ± 5 pp on the per-person denominator; specificity 87.7 % ± 2 pp on the per-alert-day denominator. The two Alavi figures are reported with their denominators named, never as a matched pair.
- **Gate C (fallback).** If Gate B fails, the discrepancy is reported as a finding, upstream code is **not** modified to close it, and all schedule comparisons are anchored to our own S1 reference arm, which is internally valid regardless.

### 18.2 Related work — quickest change detection

The data-efficient quickest-change-detection literature (Banerjee & Veeravalli, and the on-off observation-control literature more broadly) already studies when to observe under an observation cost and a false-alarm constraint. It is cited in Related Work and the framing is explicit:

> We do not claim to introduce the idea of choosing when to observe under an observation budget; that problem is well studied in sequential analysis. Our contribution is the empirical evaluation of concrete time-of-day acquisition schedules for wearable infection detection under **measured hardware-energy** constraints, on public cohorts, at a fixed alert budget.

No QCD-optimal schedule is added to the experiment (§0.3).

---

## 19. Data use and institutional requirements

This study uses previously collected, de-identified public datasets together with bench characterisation of laboratory hardware, and involves no new human-subject recruitment, no intervention and no contact with participants.

**Institutional requirements for secondary analysis of public human-subject data will be checked with the relevant institutional office and the outcome reported in the paper.** The claim "no ethics approval is required" is not made. Redistribution terms are also unresolved: neither Stanford archive states a licence, so any derived data deposited alongside the paper will be limited to aggregate results and code unless the terms are clarified.

---

## 20. Reproducibility requirements

- `data_raw/` is immutable and read-only from creation.
- Every result is generated by code; every figure regenerable by `make figures` from `results/` alone.
- Recorded at freeze: package versions, OS, Python version, git commit, all random seeds, dataset SHA-256 checksums, hardware firmware commit.
- No number enters the paper unless it traces to a machine-readable file in `results/`.
- `tests/test_causality.py` asserts that no statistic used on day *d* reads any timestamp ≥ *d*, and runs in CI on every commit.

---

## 21. Deviation register

Any departure from this document after the freeze tag is recorded in `docs/deviations.md` with: date, section, what changed, why, who decided, and whether it was made before or after the affected result was seen. The register is published with the paper.
