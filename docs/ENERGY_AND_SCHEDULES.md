# Modelled energy and sampling schedules

*Publication-stage guide, written on 24 September 2026 for research I designed and conducted. It explains how I modelled schedule energy, how the E3 budget became seven ten-minute bursts, and how each sampling schedule places those bursts. It is new explanatory writing. The code, configuration and audit output it points to are byte-identical to the versions I preserved during the research process; I have not retrospectively edited them for publication.*

## 1. What is modelled, and what is not

Energy in this study is **modelled, not measured**. [Amendment A4](prereg-v1.2-amendment-A4-no-hardware.md) replaced the planned bench measurement with a component-level model of a reference sensing architecture, and the [energy scope guide](ENERGY_SCOPE.md) sets out what that model can and cannot support. No current, power or battery life was measured on any device. The [historical bench protocol](../hardware/measurement_protocol.md) was never executed.

The model's only job in the analysis is to convert an energy budget into a whole number of ten-minute heart-rate bursts per day, so that the schedules compared under a budget cost the same modelled energy. The outcome comparison never reads an energy value.

## 2. The model

[`src/energy_model.py`](../src/energy_model.py) computes the **schedule-attributable rail-level energy per day**, `E_sched`, for a schedule running *n* bursts of *L* minutes:

```text
E_sched = n × (E_wake + E_settle)
        + (n × L × 60 s) × P_active_increment
        + E_act(arm)
        + N_tx_per_day × E_BLE
        + E_log_day
```

Every term is an increment **above platform idle** over its own interval, in joules, watts and seconds. Platform idle is charged once, across the whole 86,400-second day, only when total rail energy is needed; it cannot enter `E_sched` twice.

`E_act` is the activity-sensing cost:

- **Clock-driven arms** (S1, S2, S3, S5) sense activity only during their own bursts. Because the configuration records that the accelerometer is already included in `P_active_increment`, this term is zero for them.
- **Rest-conditional arms** (S4, S3r, S6) must know rest state while the heart-rate sensor is off, so they pay a low-power accelerometer for the rest of the day, `(86,400 s − active time) × P_accel_lp`, plus one trigger evaluation per minute, `1,440 × E_mcu_eval`.

The module refuses to compute until a frozen parameter set is loaded, so no placeholder value can reach a result. It also defines a battery-side quantity with conversion losses and a battery-life function. **Neither was used in the analysis**: the supply-architecture values they require were never set, and no battery life is reported anywhere in this repository.

## 3. The frozen parameters

[`configs/modelled_energy_scenarios.json`](../configs/modelled_energy_scenarios.json) is marked `PRE_OUTCOME_FROZEN` and dated 2 September 2026. It holds eleven parameters in each of three scenarios. The sources of each value are recorded in the [parameter provenance record](modelled_energy_parameter_provenance.md).

| Parameter | Unit | LOW | CENTRAL | HIGH |
|---|---|---|---|---|
| `E_wake` | J per burst | 0.00066 | 0.008415 | 0.05115 |
| `E_settle` | J per burst | 0.001378 | 0.02181 | 0.10701 |
| `P_active_increment` | W during a burst | 0.06891 | 0.08724 | 0.10701 |
| `P_platform_idle` | W | 0.00005076 | 0.00005076 | 0.00005076 |
| `P_accel_lp` | W outside bursts | 0.000033 | 0.000066 | 0.000231 |
| `P_accel_active` | W during a burst | 0.00165 | 0.00165 | 0.00165 |
| `E_mcu_eval` | J per evaluation | 0.000033 | 0.0001683 | 0.001023 |
| `E_BLE` | J per daily transmission | 0.02145 | 0.2145 | 2.145 |
| `E_log_day` | J per day | 0 | 0 | 0 |
| `N_tx_per_day` | count | 1 | 1 | 1 |
| `accel_included_in_active_increment` | flag | true | true | true |

The same file fixes the budgets as fractions of the continuous reference — E1 = 0.20, E2 = 0.10, **E3 = 0.05** (primary), E4 = 0.02 — the burst length of 10 minutes, and a matching tolerance of ±5%. The continuous reference is S1 treated as one 1,440-minute acquisition interval.

`P_accel_active` is carried in every scenario but contributes nothing, because the flag records that in-burst accelerometer cost is already inside `P_active_increment`. That flag is what prevents the accelerometer from being counted twice.

## 4. From budget to bursts

[`src/modelled_energy_match.py`](../src/modelled_energy_match.py) computes the reference energy for each scenario, multiplies it by each budget fraction, and for every burst-based arm chooses the whole number of bursts whose `E_sched` is **nearest** the target, up to that arm's placement capacity. A choice counts as matched only if it lies within ±5% of the target. The result is the audit record [`results/modelled_energy_match_audit.json`](../results/modelled_energy_match_audit.json), marked `PRE_OUTCOME_ENERGY_MATCH_AUDIT`.

For the primary E3 budget:

| Scenario | Reference `E_sched` (J/day) | E3 target (J/day) | Bursts, every arm | Error, clock-driven arms | Error, rest-conditional arms |
|---|---|---|---|---|---|
| LOW | 5,953.85 | 297.69 | 7 | −2.77% | −1.84% |
| CENTRAL | 7,537.78 | 376.89 | 7 | −2.67% | −1.16% |
| HIGH | 9,247.97 | 462.40 | 7 | −2.10% | +2.33% |

Every arm resolves to **seven ten-minute bursts in all three scenarios**, and all eighteen arm-scenario combinations lie within tolerance. The E3 schedules are therefore identical across LOW, CENTRAL and HIGH. That is why a single CENTRAL outcome analysis was run: separate LOW and HIGH outcome analyses would have evaluated the same masks, and none was performed.

The audit covers the other budgets too, for completeness. E1 and E2 match within tolerance in every scenario. E4 does not: at two per cent of the reference, no whole number of bursts lands within ±5% of the target for the rest-conditional arms in LOW and CENTRAL, or for any arm in HIGH. E4 was not used in the outcome analysis.

## 5. The schedules

[`src/schedules.py`](../src/schedules.py) turns a participant-day into a boolean mask over its 1,440 minutes. A burst retains a minute only if that minute has at least one recorded heart-rate sample, so a schedule's *delivered* minutes can be fewer than its *scheduled* minutes. Nighttime is 00:00–06:59 by local clock time (420 minutes) and daytime is 07:00–23:59 (1,020 minutes). A rest minute is one with a recorded step count of zero. A minute with no step record is **not** rest.

| Arm | Role | Placement at E3 (seven 10-minute bursts) |
|---|---|---|
| S1 | Continuous reference | Every observed minute. Not a burst schedule and not energy-matched. |
| S2 | Evenly spaced | Fixed 205-minute stride from midnight: 00:00, 03:25, 06:50, 10:15, 13:40, 17:05, 20:30. Three of the seven fall inside 00:00–06:59. |
| S3 | Fixed nighttime | Fixed 60-minute stride from midnight: 00:00, 01:00 … 06:00. All seven inside the night window. |
| S5 | Seeded random | Non-overlapping starts drawn across the day. The random seed is derived from a fixed global seed, the participant identifier and the date, so every mask is reproducible. |
| S4 | Rest-triggered | A causal scan from midnight: a burst starts once rest has held for five minutes, followed by a 30-minute pause. It never looks ahead, as a real device could not. |
| S3r | Nighttime, rest only | Bursts spread as evenly as possible over night starts whose whole ten minutes are rest. |
| S6 | Daytime, rest only | The same placement over daytime rest-only starts, with no top-up from active minutes. |

S3 is a **fixed clock window**, not each participant's sleep. The primary comparison H1 therefore sets seven nighttime bursts against three nighttime and four daytime bursts.

S3r and S6 are **counterfactual constructs**, not deployable schedules. Their placement reads the whole day's rest pattern in advance, which no real device can do. They exist for the M1 comparison, which asks whether any nighttime advantage survives when both arms sample only rest. For each day, M1 runs both at the same count *N′*: the smaller of the maximum number of non-overlapping night rest bursts, the maximum number of day rest bursts, and the budget of seven. A day with *N′* below two is recorded as unavailable for M1 rather than filled in. The placement routine guarantees exactly *N′* bursts whenever *N′* is feasible.

Everything in this module is deterministic. The only randomness is S5's, and it is seeded.

## 6. What was checked for this publication

On 24 September 2026 I re-ran the matching audit's calculation from the published code and configuration, in a fresh Python 3.13 environment. The recomputed audit, serialised the way the module writes it, is byte-for-byte identical to the archived record. I did not regenerate the archived file; the published copy is the preserved one. The published code, configuration and audit file each hash identically to the versions I preserved during the research.

The energy and schedule modules are exercised by the historical test suite. Its run for this publication is recorded in the [pipeline and tests guide](PIPELINE_AND_TESTS.md#4-the-test-suite).

## 7. What this does not establish

- No hardware was built or measured, and no battery life or percentage saving is claimed.
- The parameters describe one reference architecture, drawn from manufacturer specifications plus prespecified engineering uncertainty ranges. A different device would have different values, and possibly a different burst count.
- Energy matching is exact only to within ±5% and to whole bursts.
- The schedules are compared on retrospective data. S3r and S6 could not run in real time.
