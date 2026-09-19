# Energy scope: what "energy-matched" means in this study

*Publication-stage guide, written on 19 September 2026. It explains the energy quantity the executed study used, what that quantity does not establish, and how the programme written into amendment A4 differs from what was actually run. The amendment, the parameter provenance record and the historical hardware protocol are published unchanged alongside it; this guide is new explanatory writing and is not part of the historical record.*

## The short version

Schedules are matched on **modelled schedule-attributable rail-level energy**: a number produced by an equation from datasheet values and declared engineering assumptions. For this study no current was measured, no battery was discharged, and no prototype was built or validated. Nothing published here shows that a real wearable runs longer under one sampling schedule than another.

## Two questions that are easy to merge

| Question | What would answer it | Status in this study |
|---|---|---|
| Do two schedules cost the same energy on a modelled reference architecture? | a closed-form energy model with frozen parameters | Answered, within a declared ±5% tolerance |
| How long does a physical wearable run on a battery under each schedule? | bench measurement on hardware | Not attempted; removed from the study by amendment [A4](prereg-v1.2-amendment-A4-no-hardware.md) |

The confirmatory comparison needs only the first question: it asks whether *when* you sample changes pre-symptomatic warning once every schedule is held to the same energy cost. The second question is the one a reader is most likely to assume was answered, and it was not.

## What the two qualifying words mean

**Schedule-attributable** — only the energy that changes with when and how often the device wakes to acquire. Terms that are identical in every arm cannot distinguish the schedules: one daily BLE summary transmission is charged to every arm alike, and out-of-burst logging is set to zero in the confirmatory model.

**Rail-level** — the accounting happens at the 3.3 V supply rail, downstream of any regulator. Battery or input-side energy would additionally need a conversion efficiency and a usable-capacity fraction, neither of which this study establishes. That is why A4.8 removes precise battery-life estimates from the confirmatory analysis rather than reporting them with a caveat.

A4.3 states the quantity:

`E_sched = n_bursts(E_wake + E_settle) + T_active*P_active_increment + E_activity + N_tx*E_BLE + E_log`

The continuous reference arm S1 keeps all observed minutes and is *not* energy-matched; it is the denominator the budgets are taken from, not a competitor at the same budget.

## Where the parameters come from

Three kinds of number sit in the [parameter provenance record](modelled_energy_parameter_provenance.md), and they do not carry equal weight:

1. **Manufacturer datasheet values** — ESP32 current ranges, MAX30102 supply and shutdown currents, MPU-6050 active and low-power modes, each cited to the official document in §3.
2. **Derived component-level parameters** — the joule and watt figures in §5, computed from those datasheet values under the reference configuration in §2.
3. **Duration assumptions** — wake, PPG settle, MCU evaluation and BLE session lengths. §4 labels these "unmeasured engineering sensitivity" and says in its own words that they are not manufacturer specifications. They were not measured for this study; their uncertainty is represented by the spread between the LOW and HIGH scenarios rather than by any error estimate, and no ranking of the parameters by contribution to uncertainty is established anywhere in the archive.

LOW and HIGH are engineering sensitivity scenarios, not statistical confidence limits, and the record says so.

**Checked during publication, 19 September 2026.** All eleven derived parameters in §5 of the provenance record were compared against the frozen scenario configuration the analysis reads — 33 comparisons in total, across LOW, CENTRAL and HIGH — and every value matched exactly. The configuration file itself is not yet published; once it is, this check can be repeated from inside the repository.

## The budget ladder and the discrete-burst rule

The relative ladder is E1 = 20%, E2 = 10%, **E3 = 5% (the confirmatory primary budget)** and E4 = 2% of the modelled continuous S1 reference energy. Absolute joule figures, where they appear at all, are model outputs under the frozen parameterization.

Schedules keep the preregistered 10-minute burst length. For each scenario and budget the burst count is the integer `N` minimizing the absolute relative deviation from the target, with ties going to the lower-energy solution. A cell counts as energy-matched only when that deviation is within ±5%; otherwise it is labelled `DISCRETE_GRANULARITY_INFEASIBLE` and neither the tolerance nor the burst length is changed to rescue it.

Transcribed from the archived pre-outcome feasibility audit (a result file that is not yet published): at E3 the recorded deviations lie between −2.8% and −2.1% in the three scenarios, all within tolerance; the exploratory E4 cell in the HIGH scenario is recorded as `DISCRETE_GRANULARITY_INFEASIBLE` at +5.6%, and the tolerance was not relaxed to absorb it.

## What A4 planned, and what was actually run

This is the distinction most likely to be misread, so it is stated bluntly.

**Planned (A4.6).** A central literature-derived parameterization would define the primary matching, with LOW and HIGH scenarios frozen before outcome analysis, and "the schedule comparison will be repeated under all three scenarios" so that robust effects could be separated from energy-assumption-sensitive ones.

**What happened.** The pre-outcome feasibility audit found that at E3 the integer burst count resolves to **seven bursts in LOW, CENTRAL and HIGH alike**. The energy scenario reaches the schedules only through that burst count, so all three scenarios generate identical schedule masks; repeating the outcome analysis under each would have re-run identical inputs. Amendment A5 therefore fixes the confirmatory execution cell at CENTRAL / E3 / seven bursts and derives energy-model robustness from the frozen feasibility audit together with that single outcome analysis.

**What is therefore not claimed.** Separate LOW and HIGH *outcome* analyses were never performed, and no result from such runs exists or is reported anywhere in this repository. "The same schedules would have been produced under LOW and HIGH" is a statement about the energy model; it is weaker than "the finding reproduced under three energy parameterizations", which is not claimed. A reader who wants the stronger claim should treat it as untested.

A5 is not yet published; the account above was checked against the archived amendment and will link to it once that document is in the repository.

## Claims amendment A4 rules out

A4.8 and A4.9 forbid stating or implying that this study built or validated a wearable prototype, measured NodeMCU-32S, MAX30102, MPU-6050 or BLE energy, measured conversion efficiency, validated the energy model against a physical trace, or established a measured number of battery days. Physical validation is named as future work. This repository holds to that: where energy appears in the [results and limitations](RESULTS_AND_LIMITATIONS.md), it is modelled energy.

## The historical hardware protocol

The bench protocol those prohibitions replaced is published unchanged at [`hardware/measurement_protocol.md`](../hardware/measurement_protocol.md), with an [adjacent note](../hardware/README.md) explaining that it was planned and cancelled rather than executed.

## Where each rule is written

| Rule | Source |
|---|---|
| Research question reworded from measured to modelled energy | A4.2 |
| The matched quantity and its formula | A4.3 |
| Budget ladder E1–E4 | A4.4; provenance record §6 |
| Parameter provenance requirements and source hierarchy | A4.5 |
| LOW / CENTRAL / HIGH scenarios | A4.6; provenance record §4 |
| Activity-sensing accounting and anti-double-counting | A4.7 |
| Battery-life claims removed | A4.8 |
| Prohibited hardware claims | A4.9; provenance record §8 |
| Scope of the confirmatory claim | A4.10 |
| Freeze gate before outcomes were inspected | A4.11 |
| Integer 10-minute burst matching and the ±5% feasibility rule | A4.13; provenance record §6 |
| Derived parameter values | provenance record §5 |
| Confirmatory execution cell actually run | A5 (not yet published) |
