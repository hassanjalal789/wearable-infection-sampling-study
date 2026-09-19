# Preregistration amendment A1 — prereg v1.1 → v1.2

**Status: DRAFT — NOT FROZEN.** Issued 31 August 2026 following the Phase-0 correction
review. The sections below **replace in full** the correspondingly numbered sections of
prereg-v1.1. Everything not listed here is unchanged.

---

## Replaces §9 — Primary endpoint

**Pre-symptomatic detection** := a first qualifying alert on a day in **[onset − 21,
onset − 1]**. Warning = (onset date − first qualifying alert date) in whole days, and is
therefore **≥ 1 by definition**.

An alert on the onset date itself is **same-day detection**. It is *not* pre-symptomatic,
it does not count toward the primary endpoint, and it is tabulated separately.

For comparability with Mishra et al. and Alavi et al., who report detection "at or before
symptom onset", a secondary descriptive statistic over the window [onset − 21, onset] is
also reported, clearly labelled as the at-or-before definition.

*Reason for the change.* prereg-v1.1 used [onset − 21, onset], which admits a 0-day
"pre-symptomatic" warning — a contradiction in terms that also made the simulated endpoint
differ from the analysed one. The endpoint and the simulation now share one definition.

### Precision for the paired warning-time difference

The paired difference in warning days is defined on the **detected-under-both subgroup**
and its confidence interval is bootstrapped over **that subgroup only**. Non-detections are
never zero-imputed into this estimate.

Two consequences are stated in Methods rather than left implicit:

1. Zero-imputation attenuates the estimate toward zero and mixes a detection effect into a
   warning-time effect. Unit test `test_zero_imputation_attenuates_the_warning_time_effect`
   demonstrates the attenuation on synthetic data (true +1.0 day recovered by the subgroup
   estimator; the zero-imputed estimator returns under 60 % of it at a 55 % detection rate).
2. The detected-under-both subgroup is a **post-hoc, outcome-dependent subgroup**. The
   estimate is descriptive and is not interpreted causally. The confirmatory quantity
   remains θ from the hierarchical win/loss comparison, which uses every participant.

---

## Replaces §5.b — Minimum historical calibration data, and the C_min decision rule

**Use ALL eligible historical negative `z`-defined days available before the evaluation
window**, subject to a prespecified minimum C_min. The 28-day cap in prereg-v1.1 is removed.

### Why the v1.1 minimum of 14 days was inadequate

With C valid calibration days, the achieved alert rate A(τ) can only take the values
k · 30.44 / C for integer k. One alert therefore contributes 30.44/C alert-days per
person-month, so the budget constraint is quantised, and at short C it collapses.

| C (days) | one alert = /person-month | number of admissible alert-count levels including zero, B=1 | B=2 | B=4 |
|---|---|---|---|---|
| 14 | 2.174 | 1 | **1** | 2 |
| 21 | 1.450 | 1 | 2 | 3 |
| 28 | 1.087 | **1** | 2 | 4 |
| 42 | 0.725 | 2 | 3 | 6 |
| 61 | 0.499 | 3 | 5 | 9 |
| 91 | 0.335 | 3 | 6 | 12 |

At C = 14 the primary budget B = 2 admits exactly **one** value — zero alerts. The
constraint is then not "≤ 2 alert-days per person-month" but "no alert at all in the
calibration window", which is a stricter and participant-varying operating point than the
one preregistered. At C = 28 the B = 1 sensitivity has the same defect.

A value of 1 in those columns means **only zero alerts is admissible**, not that one alert is permitted. Minimum C for a single alert to be admissible at all: **B=1 → C ≥ 31; B=2 → C ≥ 16;
B=4 → C ≥ 8.** For three admissible levels: B=1 → C ≥ 61; B=2 → C ≥ 31; B=4 → C ≥ 16.

### Frozen decision rule for C_min — availability only

```
C_min := max { c in {28, 42, 61, 91} : share of eligible participants with C_p >= c
                                       is at least 0.80 },   default 28 if none qualifies
```

Implemented in `src/calibration_resolution.py::choose_c_min`. It reads **only** the
distribution of available calibration days. It cannot see any alert, any schedule output or
any comparison. It is executed once, immediately after the eligibility audit, and its
output is written to `results/calibration_rule.json` and frozen.

### Reported before freezing

Distribution of calibration days per participant — median, IQR, minimum, maximum, the full
histogram — together with the implied one-alert resolution at the median, and the retention
share at each candidate C_min.

### Reported per participant in the results

`C_p`, the resolution 30.44/C_p, the selected τ_p, the achieved A(τ_p), and a
`coarse_calibration` flag when 30.44/C_p exceeds B/2. A sensitivity analysis restricted to
participants with 30.44/C_p ≤ B/2 is added to §16.

---

## Replaces §7.1–7.5 — Schedule naming and deterministic placement

### S2 is renamed

**S2 = uniform-block duty cycling**: N equally spaced 10-minute bursts across the 24-hour
day, stride ⌊1440/N⌋ from 00:00. The original 1-in-n **single-minute** baseline is **not
implemented**, is **not** the primary baseline, and must not be described as such anywhere
in the paper. Its removal is deliberate: a 1-in-n minute mask makes RHR-Diff structurally
undefined at every duty cycle, so it could not serve as a shared baseline.

### Placement families, stated explicitly

| Family | Arms | Placement | Uses lookahead? |
|---|---|---|---|
| Clock-driven | S2, S3 | fixed stride from the window start | No |
| Reactive trigger | S4 | earliest-first causal scan, 5-minute rest hold, 30-minute skip | No |
| Counterfactual matched | S3ʳ, S6 | even-spread nearest-eligible over rest-only starts | **Yes** |
| Seeded random | S5 | non-overlapping starts, rejection sampled, per-day seed | No |

**S3ʳ and S6 are analysis constructs for the M1 mechanism test, not deployable schedules.**
Their placement uses an oracle over the day's rest pattern that no real device possesses,
and their energy is accounted as if the device ran continuous activity sensing. This is
stated as a limitation of M1 in the paper. S4, by contrast, is deliberately greedy and
causal, because a triggered device cannot see the future.

### Deterministic placement for S3ʳ and S6 when eligible locations exceed N′

An eligible start is a minute *m* such that [m, m + L − 1] lies wholly inside the window and
every minute in it is rest. Given the eligible list and a target count N′:

```
for i = 0 .. N'-1:
    target_i = window_start + (i + 0.5) * window_length / N'
    floor_i  = (last chosen start + L)  if any chosen, else window_start
    candidates = { e in eligible : e >= floor_i }
    if candidates is empty: break
    choose the candidate minimising (|e - target_i|, e)      # ties -> smaller minute
if fewer than N' chosen:
    top up earliest-first from remaining starts that clear every chosen start by >= L
```

No randomness and no seed. Ties break to the smaller minute. Overlap is impossible by the
`floor_i` construction and by the top-up guard. Verified bit-for-bit by
`test_even_spread_is_reproducible_and_ordered` and `test_deterministic_bit_for_bit`.

Maximum feasible counts use optimal earliest-first interval packing
(`_max_packing`), so N′ = min(pack(night rest starts), pack(day rest starts), N_budget) is
the true feasible maximum and the even-spread pass rarely under-fills.

### Unchanged and reaffirmed

Bursts never overlap in any arm. Burst length is exactly L = 10 minutes. Unspent energy is
permitted, never carried between days, and always recorded. S2, S3, S3ʳ, S5 and S6 receive
identical N at equal energy when their E_act terms match; S4 may differ, and that difference
is reported rather than corrected. Energy is charged for **scheduled** bursts in the primary
analysis; delivered-burst charging remains a sensitivity.

---

## Replaces §8.1–8.4 — Whole-system energy and battery-side accounting

### The acquisition term is a whole-system increment

```
P_active_increment = P_whole_system_active − P_platform_idle
```

measured on the actual NodeMCU-32S board at the 3.3 V rail **during a burst**. It therefore
already contains MCU active processing, the MAX30102 including LED current, I2C traffic and
any logging inside the burst. A sensor-only `P_PPG` term is **not** used, because it omits
the MCU cost that every burst actually pays.

```
E_sched(S) = N_bursts * (E_wake + E_settle)
           + T_active  * P_active_increment
           + E_act(S)                      # option B, per §8.2, unchanged
           + N_tx * E_BLE                  # N_tx = 1/day, constant for every arm
           + E_log_day                     # included only if materially non-zero
```

### Two energies, never mixed

- **A. Rail-level (3.3 V) energy** — the quantity schedules are matched on.
- **B. Battery / input-side energy** — the quantity battery life is computed from,
  including regulator or boost losses, or measured directly at the cell terminals.

**Battery-days are never computed from a downstream 3.3 V figure while ignoring conversion
losses.** `src/energy_model.py` enforces this in code: `battery_days()` routes through
`e_total_input_joules()`, which divides by a measured `eta_conversion`, and
`SupplyArchitecture` raises unless `path`, `eta_conversion` and `usable_fraction` are all
set from measurement.

### Supply architecture is documented, not assumed

The AMS1117 on a NodeMCU-32S cannot regulate from a single Li-Po — ~1.1 V typical dropout
and a 10 mA minimum load. Exactly one path is built and recorded:
`ldo_direct_3v3` (Li-Po → TP4056 → ME6211/HT7333 → the 3V3 pin, AMS1117 bypassed) or
`boost_5v_then_ams1117` (two conversions in series). `eta_conversion` is measured under a
representative burst-plus-idle duty pattern, not taken from a datasheet.

### Measurement paths

Two arrangements, because no single shunt spans 10 µA to 150 mA: 0.1 Ω with narrow PGA and
9-bit/84 µs conversions for the active path (15 mV burden at 150 mA, 100 µA/LSB); 10 Ω with
64–128 sample averaging on a **non-waking firmware build** for the sleep path (47 mV burden
at 4.7 mA, 1 µA/LSB), cross-checked with a µA-range DMM. Full protocol in
`hardware/measurement_protocol.md`. Published values are context only and may substitute
for a measurement solely with a documented failure entry in `hardware/measurement_log.md`.

---

## Replaces §15 — Power, MDE and precision

```
Power / MDE / expected CI width = [TO BE FILLED AFTER THE ELIGIBILITY AUDIT]
```

### Dependence is swept, not estimated

**Cross-schedule dependence is not identifiable from a single S1 arm** and is therefore not
estimated from one. A preregistered **sensitivity grid** over within-participant dependence
is swept instead, and MDE and expected precision are reported **across the whole grid**:

| Label | ρ_detection (tetrachoric) | ρ_warning-time |
|---|---|---|
| independent | 0.00 | 0.00 |
| low | 0.25 | 0.25 |
| moderate | 0.50 | 0.50 |
| high | 0.75 | 0.75 |

The S1 reference arm **may** inform the **marginal** baseline detection probability p_B,
provided this is done before any schedule-comparison result is inspected and the use is
logged. `src/power_sim.py --p-b <value> --log-baseline results/power_inputs/baseline.jsonl`
writes a provenance record naming the source and stating that dependence was *not* taken
from S1.

### Committed with this amendment

`src/power_sim.py` (v2), seed 20261010, 4,000 Monte Carlo runs per cell, exact binomial sign
test on the hierarchical win/loss, warning window [1, 21] days, detected-under-both
precision, and the dependence grid above. The script's SHA-256 is written into every
output file. Unit tests in `tests/test_power_sim.py`.

### Reporting

The study is reported as an **estimation study**. MDE and expected interval widths are
stated in the abstract, across the dependence grid rather than at a single assumed
correlation. The phrase "adequately powered" is not used.
