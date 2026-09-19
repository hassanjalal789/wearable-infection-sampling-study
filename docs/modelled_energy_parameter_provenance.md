# Modelled-Energy Parameter Provenance Table

**Project:** Energy-Matched Heart-Rate Sensing Schedules for Pre-Symptomatic Infection Detection on Low-Cost Wearables  
**Amendment:** A4 — no-hardware / modelled-energy design  
**Status:** PRE-OUTCOME FROZEN PARAMETERIZATION  
**Date:** 2026-09-02

## 1. Scope

This study does not physically measure wearable power. The energy comparison is a transparent **component-level model** parameterized from manufacturer specifications plus prespecified engineering uncertainty ranges.

No value below may be described as measured by this study.

The confirmatory comparison uses schedule-attributable modelled energy. Precise battery-life claims are outside the confirmatory analysis.

## 2. Reference acquisition configuration

- MCU family: original ESP32 series.
- HR acquisition: CPU operational at 80 MHz with radio disabled during acquisition.
- PPG: MAX30102, heart-rate mode, 50 samples/s, 215.44 µs pulse width.
- MPU-6050 accelerometer runs during HR bursts and is included in active acquisition energy.
- Rest-conditional schedules pay low-power accelerometer overhead outside HR bursts.
- One identical BLE summary-transmission event is charged per day to every arm.
- `E_log_day = 0` for the confirmatory model.

These are modelling assumptions for a low-cost reference architecture, not a claim that a physical NodeMCU prototype was built or validated.

## 3. Manufacturer evidence

### ESP32 — Espressif ESP32 Series Datasheet

Relevant values:
- 80 MHz, dual-core, CPU operational / modem-sleep range: 20–31 mA.
- Deep-sleep with RTC timer + RTC memory: 10 µA.
- BT/BLE transmit at 0 dBm: 130 mA.
- BT/BLE receive/listening: 95–100 mA.

Official source:
https://documentation.espressif.com/esp32_datasheet_en.html

### MAX30102 — Analog Devices / Maxim MAX30102 Datasheet

Relevant values:
- VDD = 1.8 V nominal.
- VLED+ may operate at 3.3 V.
- SpO2/HR mode, pulse width ~215 µs, 50 samples/s: 600 µA typical and 1200 µA maximum VDD current.
- Shutdown current: 0.7 µA typical, 10 µA maximum.
- LED current is programmable.

Official source:
https://www.analog.com/media/en/technical-documentation/data-sheets/MAX30102.pdf

### MPU-6050 — TDK/InvenSense MPU-6000/MPU-6050 Product Specification Rev. 3.4

Relevant values:
- Accelerometer only: 500 µA typical.
- Accelerometer low-power mode:
  - 1.25 Hz: 10 µA
  - 5 Hz: 20 µA
  - 20 Hz: 70 µA
  - 40 Hz: 140 µA
- Full-chip idle: 5 µA.

Official source:
https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet.pdf

## 4. LOW / CENTRAL / HIGH scenarios

LOW and HIGH are engineering sensitivity scenarios, not statistical confidence limits.

For the rest classifier, HIGH uses the 20 Hz low-power MPU-6050 mode rather than 40 Hz. The study operates on minute-level rest state, so 20 Hz is already a deliberately conservative high-rate sensitivity setting; 40 Hz would represent a different sensing design rather than simple parameter uncertainty.

| Quantity | LOW | CENTRAL | HIGH | Provenance |
|---|---:|---:|---:|---|
| ESP32 acquisition current | 20 mA | 25.5 mA | 31 mA | ESP32 80 MHz range; midpoint central |
| MAX30102 VDD current | 0.6 mA | 0.6 mA | 1.2 mA | datasheet typical/max |
| MAX30102 peak LED current | 5.078 mA | 10.156 mA | 25.4 mA | explicit engineering sensitivity |
| MAX30102 LED pulse width | 215.44 µs | 215.44 µs | 215.44 µs | fixed |
| MAX30102 sampling rate | 50 Hz | 50 Hz | 50 Hz | fixed |
| MPU-6050 active accel | 0.5 mA | 0.5 mA | 0.5 mA | datasheet typical |
| MPU-6050 low-power accel | 10 µA @1.25Hz | 20 µA @5Hz | 70 µA @20Hz | datasheet operating modes |
| wake duration assumption | 10 ms | 100 ms | 500 ms | unmeasured engineering sensitivity |
| PPG settle duration assumption | 20 ms | 250 ms | 1.0 s | unmeasured engineering sensitivity |
| MCU evaluation duration | 0.5 ms | 2 ms | 10 ms | unmeasured engineering sensitivity |
| BLE TX-session duration | 50 ms | 500 ms | 5 s | unmeasured engineering sensitivity |

The duration assumptions are not manufacturer specifications and must never be represented as such.

## 5. Derived component-level parameters

MAX30102 LED duty fraction:

`50 * 215.44e-6 = 0.010772`

| Parameter | LOW | CENTRAL | HIGH |
|---|---:|---:|---:|
| `E_wake` J | 0.000660 | 0.008415 | 0.051150 |
| `E_settle` J | 0.001378 | 0.021810 | 0.107010 |
| `P_active_increment` W | 0.06891 | 0.08724 | 0.10701 |
| `P_platform_idle` W | 0.00005076 | 0.00005076 | 0.00005076 |
| `P_accel_lp` W | 0.000033 | 0.000066 | 0.000231 |
| `P_accel_active` W | 0.00165 | 0.00165 | 0.00165 |
| `E_mcu_eval` J | 0.000033 | 0.0001683 | 0.001023 |
| `E_BLE` J | 0.02145 | 0.2145 | 2.145 |
| `E_log_day` J/day | 0 | 0 | 0 |
| `N_tx_per_day` | 1 | 1 | 1 |
| `accel_included_in_active_increment` | true | true | true |

`P_platform_idle` is a chip/component-level reference only. It is not measured NodeMCU board sleep power and is not used to determine the confirmatory relative schedule budgets.

## 6. Budget and discrete-burst matching rule

The nominal ladder remains:
- E1 = 20% of modelled continuous S1 schedule-attributable energy
- E2 = 10%
- E3 = 5% — primary confirmatory budget
- E4 = 2% — low-budget exploratory stress test

Schedules retain the preregistered **10-minute burst definition**. No fractional or shortened bursts are introduced solely to make the energy arithmetic fit.

For each scenario, budget, and energy-accounting family, choose the integer burst count `N` that minimizes absolute relative deviation from the nominal target. Ties select the lower-energy solution.

A cell is energy-match feasible when:

`abs(E_achieved / E_target - 1) <= 0.05`

E1, E2 and especially primary E3 must satisfy this rule for a result to be described as energy-matched.

E4 is intentionally near the granularity limit of 10-minute blocks. If no integer burst count meets ±5%, the cell is reported as **DISCRETE_GRANULARITY_INFEASIBLE** rather than changing burst duration or silently relaxing the tolerance.

## 7. Robustness interpretation

The CENTRAL parameterization defines the primary modelled-energy analysis.

LOW and HIGH are mandatory energy-model sensitivity scenarios for E3.

An E3 schedule advantage is called **energy-model robust** only if:
1. E3 is feasible within ±5% in LOW, CENTRAL and HIGH scenarios; and
2. the substantive direction persists in all three.

## 8. Prohibited language

Do not state or imply that these values were:
- measured on the project's ESP32/NodeMCU board;
- measured on a MAX30102/MPU-6050 prototype;
- validated against a physical current trace;
- used to establish measured battery life.
