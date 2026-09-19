# Preregistration Amendment A4 — No-Hardware / Modelled-Energy Design

**Date:** 2026-09-02  
**Status:** PROSPECTIVE — to be frozen before any schedule-performance outcome analysis  
**Project:** Energy-Matched Heart-Rate Sensing Schedules for Pre-Symptomatic Infection Detection on Low-Cost Wearables

## A4.1 Reason for amendment

The project will not perform physical hardware energy measurements. This decision is made before inspection of schedule-performance outcomes.

The previously frozen hardware measurement protocol is retained in the repository as a record of the originally planned validation procedure, but it will not be executed in this study.

No hardware measurements, battery-life measurements, or experimentally measured joule/current values will be claimed.

## A4.2 Research-question wording

Replace:

> At equal measured device energy ...

with:

> At equal modelled schedule-attributable device energy ...

The substantive comparison of sensing schedules, alert burden, presymptomatic warning, and the M1 daytime-rest control is otherwise unchanged.

## A4.3 Energy quantity used for schedule matching

The confirmatory schedule comparison uses **modelled schedule-attributable rail-level energy**:

`E_sched = n_bursts(E_wake + E_settle) + T_active*P_active_increment + E_activity + N_tx*E_BLE + E_log`

The existing energy-accounting implementation remains the computational definition.

The study will not interpret this quantity as physically measured energy from the tested device.

## A4.4 Energy budget ladder

The prespecified relative budget ladder is retained:

- E1 = 20% of the modelled S1 continuous schedule-attributable reference energy
- E2 = 10%
- E3 = 5% — confirmatory primary budget
- E4 = 2%

Absolute joule/day values, if shown, are model outputs under the frozen parameterization rather than measurements.

## A4.5 Parameter provenance

Before any schedule-performance outcomes are generated, every non-zero physical parameter used by the energy model must be entered into a provenance table containing:

- parameter name
- numerical value and units
- low / central / high scenario values
- source
- source type
- exact page/table/section where available
- hardware/configuration to which the source applies
- any conversion or calculation
- justification for transfer to the model

Source hierarchy:

1. manufacturer datasheet or official technical documentation;
2. peer-reviewed hardware/power measurement;
3. reputable engineering measurement/documentation.

No parameter may be chosen or adjusted using infection-detection outcomes.

If defensible numerical evidence cannot be found for a component, the study will use a broad prespecified sensitivity range and label the parameter uncertain rather than inventing a value.

## A4.6 Primary and sensitivity parameterizations

A central literature-derived parameterization will define the primary modelled energy matching.

Two additional scenarios will be frozen before outcome analysis:

- LOW energy-overhead scenario
- HIGH energy-overhead scenario

The schedule comparison will be repeated under all three scenarios.

The primary scientific conclusion must distinguish:

- effects robust across all three parameterizations;
- effects sensitive to energy assumptions.

## A4.7 Activity-sensing accounting

The previously specified Option B remains:

- clock-driven arms co-schedule accelerometer use with acquisition bursts;
- rest-conditional arms pay continuous low-power activity-sensing overhead outside bursts plus trigger-evaluation overhead.

The existing anti-double-counting rules remain unchanged.

Because these terms are modelled rather than bench-measured, their uncertainty must be represented in the LOW/HIGH sensitivity scenarios.

## A4.8 Battery-life claims

Precise battery-life estimates are removed from the confirmatory study.

The paper must not claim a measured or validated number of battery days.

If battery-life numbers are included at all, they must be clearly labelled illustrative model projections and placed outside the primary outcome claims.

## A4.9 Hardware claims prohibited

The paper must not state or imply that this study:

- built a validated wearable prototype;
- measured NodeMCU-32S current or power;
- measured MAX30102 energy;
- measured MPU6050 energy;
- measured BLE transmission energy;
- measured conversion efficiency;
- validated the energy model against a physical trace.

Physical validation is future work.

## A4.10 Interpretation

The confirmatory claim is limited to:

> whether acquisition timing changes presymptomatic detection performance when schedules are constrained to the same **modelled** energy budget under prespecified hardware-energy assumptions.

It is not a claim that the schedules have been proven equal-energy on a physical wearable.

## A4.11 Freeze gate before schedule outcomes

Schedule-performance outcomes must not be inspected until:

1. the literature/datasheet parameter provenance table is complete;
2. LOW/CENTRAL/HIGH parameter values are frozen;
3. E1-E4 are generated from those values;
4. energy-model tests pass;
5. this amendment and the parameter table are committed to Git.

No subsequent parameter change may be made to improve schedule-performance results. Any later correction must be documented as a post-freeze correction with its reason and effect.

## A4.12 Unchanged parts of the preregistration

This amendment does not change:

- the N=38 primary base-cohort definition;
- source-missingness handling;
- symptomatic/onset requirements;
- TOD-z primary detector;
- alert-burden cap;
- presymptomatic endpoint;
- S1-S6 schedule definitions except burst counts determined by the modelled energy budgets;
- M1 S3r versus S6 control;
- fixed-sequence gatekeeping;
- paired hierarchical primary outcome;
- statistical testing;
- Phase-2-only sensitivity;
- realized-sample-count-conditioned M1 sensitivity;
- reproduction Gate A / Gate B findings.

## A4.13 — Discrete 10-minute burst energy-matching clarification

Inspection of the preregistered schedule engine before schedule-performance analysis confirmed that S2/S3/S4/S5/S3r/S6 use integer counts of 10-minute acquisition bursts. The 10-minute schedule definition is retained; fractional or shortened bursts will not be introduced solely to force an energy match.

For each LOW/CENTRAL/HIGH parameter scenario and each nominal budget, the burst count is chosen prospectively as the integer `N` minimizing absolute relative error between modelled schedule-attributable energy and the nominal S1-derived target. Ties select the lower-energy solution.

Energy-match feasibility is defined as absolute target deviation <=5%.

E1, E2 and E3 comparisons may be described as energy-matched only when this feasibility criterion is satisfied. E3 remains the confirmatory primary budget and must satisfy the criterion in LOW, CENTRAL and HIGH model parameterizations before schedule outcomes are inspected.

E4 (2% of S1) is retained as an exploratory low-budget granularity stress test. If no integer 10-minute burst allocation meets the ±5% criterion, the affected cell is labelled `DISCRETE_GRANULARITY_INFEASIBLE`; the tolerance is not relaxed and the schedule definition is not changed.

This clarification changes only the prospective energy-allocation rule required by the integer 10-minute schedule implementation. It does not change cohort, detector, endpoint, alert burden, hypotheses, M1 matching, or statistical testing.
