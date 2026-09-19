# Historical hardware protocol — planned, superseded, never executed

*Publication-stage note, written on 19 September 2026. The protocol beside it is one I wrote earlier in the project and is published unchanged; this note is new explanatory writing and is not part of the historical record.*

[`measurement_protocol.md`](measurement_protocol.md) specifies bench measurements of wearable power — rail-level idle, wake, PPG settle, acquisition, accelerometer, trigger-evaluation, BLE and logging energy — that I **planned and then cancelled**. None of them were carried out. The file is published because it records what was intended and because it defines the accounting boundary the surviving energy model still uses, not because it reports any measurement.

## Status

Superseded by amendment [A4](../docs/prereg-v1.2-amendment-A4-no-hardware.md), dated 2 September 2026, before any schedule-performance outcome was inspected. A4.1 states the decision in its own words: the project will not perform physical hardware energy measurements, the protocol is retained as a record of the originally planned validation procedure, and no measured joule or current values will be claimed. The study's energy quantity became modelled schedule-attributable rail-level energy; see the [energy scope guide](../docs/ENERGY_SCOPE.md).

## Why "never executed" is a checkable statement, not a courtesy

- **§8 of the protocol is an empty replication record.** Every field — date, board revision, firmware commit, instrument, shunt, sampling rate, repetitions, mean, SD, anomalies — is blank. It is a form that was never filled in.
- **The preserved archive's hardware folder contains this protocol and nothing else.** Checked on 19 September 2026 during publication: no measurement JSON, no raw traces, no instrument logs, no photographs, no `RailEnergyParams` file populated from measurement.
- **§9 permits only measured values to populate `RailEnergyParams`.** Since no measurement exists, that path was never taken; the analysis instead reads a frozen scenario configuration derived from manufacturer datasheets and declared engineering assumptions, documented in the [parameter provenance record](../docs/modelled_energy_parameter_provenance.md).
- **§10's freeze rule was never satisfied.** It requires all hardware parameters measured, additivity validation completed, raw traces retained and a measurement JSON committed before energy budgets could be derived. The budgets were instead derived under A4 from the modelled parameterization.

## How to read it

The document is written entirely in the imperative and the future — *measure*, *record*, *repeat at least 30 trials*, *report mean, SD and range*. Nothing in it is a report of results. No number in it should be cited as a measurement, and its presence in this repository should not be read as evidence that a prototype existed.

What remains useful in it is the accounting discipline in §1: every event term is defined as an increment above the background state that the model represents separately, which is what keeps wake, settle, BLE and evaluation energy from being double-counted against the low-power accelerometer background. That rule survived into the modelled design.

## Related documents

- [Amendment A4](../docs/prereg-v1.2-amendment-A4-no-hardware.md) — the amendment that superseded this protocol.
- [Modelled-energy parameter provenance](../docs/modelled_energy_parameter_provenance.md) — the values the study actually used, with their sources.
- [Energy scope guide](../docs/ENERGY_SCOPE.md) — what the modelled quantity does and does not establish.
- [Results and limitations](../docs/RESULTS_AND_LIMITATIONS.md) — where the modelled-energy limitation is stated alongside the findings.
