# Hardware Energy Measurement Protocol v1

**Project:** Energy-Matched Heart-Rate Sensing Schedules  
**Status:** Pre-outcome hardware protocol  
**Primary quantity:** 3.3 V rail-level schedule-attributable energy  
**Secondary quantity:** battery/input-side energy for battery-life estimates only

## 1. Important accounting boundary

The energy model is additive only if components that are modelled separately are not included twice.

For all event terms below, measure the **increment above the background state that is represented separately in the model**.

- `P_platform_idle`: board asleep, PPG shut down, accelerometer off.
- `P_accel_lp`: extra power of low-power accelerometer above platform idle.
- `E_wake`, `E_settle`, `E_BLE`, `E_mcu_eval`: event-only increments. If an accelerometer background is running during a validation trace, subtract that background before integrating the event.
- `P_active_increment`: whole-system acquisition power minus platform idle. Record whether the accelerometer was running during this measurement using `accel_included_in_active_increment`.

This avoids double-counting low-power accelerometer energy during wake, settle, BLE and evaluation intervals.

## 2. Rail measurement setup

For the primary rail-level comparison, measure downstream at 3.3 V.

Preferred setup:
1. Use a regulated 3.3 V bench supply connected to the board 3V3 pin.
2. Do not simultaneously power the board from USB/5 V.
3. Place the current measurement device in series with the 3.3 V supply.
4. Use a common ground for supply, board, sensors and measurement equipment.
5. Record actual rail voltage during every trial.

If the available meter cannot resolve both microamp/milliamp sleep current and short high-current radio/wake events, use separate measurement ranges/instruments. Do not force one shunt value to cover all states.

For short events (wake/BLE), if the instrument bandwidth is insufficient, execute the identical event repeatedly (for example 100 times), integrate the total energy, then divide by the number of events.

## 3. Firmware markers

Use GPIO markers or serial timestamps to delimit:

- wake start
- firmware-ready
- PPG power/config start
- first valid PPG sample
- acquisition end
- MCU evaluation start/end
- BLE start/end

The measurement boundaries must match these markers exactly.

## 4. First valid PPG sample

Before measurement, freeze an operational validity rule. Recommended rule:

A sample is the first valid PPG sample when:
1. the optical reading is non-zero and not ADC-saturated,
2. it lies inside the sensor's configured usable range,
3. it is followed by at least 1 second of continuously valid samples under the same rule.

Use the same rule in every settle trial. Record the final rule in firmware and this protocol before collecting energy values.

## 5. Measurements

### M1 — Platform idle

Configuration:
- MCU deep sleep
- MAX30102 shut down
- accelerometer off
- BLE off
- no out-of-burst logging

Measure at least 5 runs of 60 s after the board has reached steady state.

Compute:

`P_platform_idle = mean integral(P(t) dt) / duration`

Report mean, SD and range.

### M2 — Low-power accelerometer

Configuration identical to M1 except accelerometer is in the exact low-power mode used by S3r/S4/S6.

Measure at least 5 runs of 60 s.

Compute:

`P_accel_lp = P(idle + accel-low-power) - P_platform_idle`

This value is an increment above platform idle.

### M3 — Wake event

Use the common decomposition state with the separately-modelled accelerometer disabled.

Boundary:
- start: deep-sleep exit
- end: firmware ready immediately before PPG power/configuration

Repeat at least 30 independent wakes. If using a low-bandwidth meter, use repeated-event batches.

Compute each event:

`E_wake = integral[(P(t) - P_platform_idle) dt]`

Report median, mean, SD and 95% range.

### M4 — PPG settle event

Boundary:
- start: MAX30102 power/configuration begins
- end: first valid PPG sample under the frozen validity rule

Accelerometer disabled for the common event decomposition.

Repeat at least 30 trials with the same sensor placement/load.

Compute:

`E_settle = integral[(P(t) - P_platform_idle) dt]`

Also report settle duration distribution.

### M5 — Active acquisition

After settling, run the actual burst firmware and MAX30102 settings.

Measure at least 30 stable windows of >=60 s.

Compute:

`P_active_increment = P_whole_system_active - P_platform_idle`

This must include:
- active ESP32 processing
- MAX30102 including LED current
- I2C traffic
- normal within-burst logging

Record explicitly whether the accelerometer is running in these trials:

`accel_included_in_active_increment = true/false`

### M6 — Active accelerometer increment

Measure the acquisition state both with and without the accelerometer using otherwise identical firmware.

Compute:

`P_accel_active = P(active with accel) - P(active without accel)`

Measure this even if the final model flag makes the value unused; it is a useful cross-check.

### M7 — MCU rest-trigger evaluation

Use the low-power accelerometer background that S3r/S4/S6 actually require.

Run a batch of at least 1,000 trigger evaluations without activating PPG.

Compute:

`E_mcu_eval = [E(batch) - E(background over same duration)] / number_of_evaluations`

The default model assumes 1,440 evaluations/day. If firmware does not evaluate once per minute, change the model only before schedule outcomes and document the actual fixed frequency.

### M8 — BLE daily transmission

Freeze one payload and transmission behaviour that is identical for every schedule arm.

Prefer at least 100 repeated transmissions.

Compute:

`E_BLE = [E(batch) - E(background over same duration)] / number_of_transmissions`

Use `N_tx_per_day = 1` only if the implemented protocol truly sends exactly one equivalent daily summary for every arm.

### M9 — Out-of-burst logging

Inspect firmware.

If there is no storage write, LED indication, serial output or other logging outside acquisition bursts:

`E_log_day = 0`

Otherwise measure the daily incremental energy and enter the measured value. Do not leave zero merely because it is the software default.

## 6. Additivity validation

After measuring all components, build at least one complete physical daily-pattern trace or accelerated equivalent for:

- one clock-driven arm (S2 or S3)
- one rest-conditional arm (S4 or S6)

Compare directly integrated rail energy against the closed-form energy model.

Target agreement: within measurement uncertainty and preferably <=5%.

If the discrepancy is >5%, do not tune values to force agreement. Identify the missing/overlapping physical state and amend the accounting before running schedule outcomes.

## 7. Battery/input-side measurements

Battery life is secondary and must not be calculated from the 3.3 V rail alone.

Record the actual supply path, for example:
- direct regulated 3.3 V path, or
- boost to 5 V followed by the board regulator.

Measure input and rail power under at least:
- platform idle
- low-power accelerometer background
- active acquisition
- BLE event

A single `eta_conversion` may be used only if it is defined as a measured schedule-representative effective efficiency. Otherwise report a range or omit precise battery-day claims.

Also measure/justify `usable_fraction` of the battery capacity to the selected cutoff voltage.

## 8. Replication record

For every measurement retain:

| Field | Record |
|---|---|
| date/time | |
| board model/revision | |
| ESP32 firmware commit/hash | |
| MAX30102 module | |
| accelerometer module | |
| supply voltage | |
| measurement instrument | |
| shunt/range | |
| sampling rate | |
| sensor settings | |
| LED current/settings | |
| accelerometer mode | |
| BLE payload bytes | |
| repetitions | |
| raw trace filename | |
| mean | |
| SD | |
| median | |
| minimum/maximum | |
| notes/anomalies | |

## 9. Values that may enter `RailEnergyParams`

Only measured values may populate:

- `E_wake`
- `E_settle`
- `P_active_increment`
- `P_platform_idle`
- `P_accel_lp`
- `P_accel_active`
- `E_mcu_eval`
- `E_BLE`
- `E_log_day`
- `accel_included_in_active_increment`

Synthetic constants in unit tests are never hardware evidence.

## 10. Freeze rule

Do not calculate E1-E4 or inspect schedule-performance outcomes until:

1. all required hardware parameters are measured,
2. additivity validation is completed,
3. raw measurement traces are retained,
4. the measurement JSON is committed,
5. all regression tests pass.

After that, derive E1-E4 from measured schedule-attributable rail energy and freeze them before the primary schedule outcome analysis.
