#!/usr/bin/env python3
"""
Component-level modelled-energy accounting. PREREGISTRATION ARTEFACT, v3 (A4 no-hardware).

The acquisition term measures the INCREMENTAL ACTIVE WHOLE-SYSTEM cost during a
burst, not sensor-only power:

    P_active_increment = P_whole_system_active - P_platform_idle

modelled for the frozen component-level reference architecture while a burst runs.
It therefore already contains MCU active processing, the MAX30102 including LED
current, the I2C traffic and any logging that happens inside the burst.

Two energies are kept strictly separate:
  A. RAIL-LEVEL (3.3 V) energy      -> used for the schedule comparison
  B. BATTERY / INPUT-SIDE energy    -> used for predicted battery life, and it
                                       must include conversion losses

EVERY physical constant below is PARAMETER-PENDING. The module refuses to compute
until a frozen modelled parameter set is loaded, so no placeholder can reach a result.
"""
from __future__ import annotations
from dataclasses import dataclass
import json

PENDING = None


@dataclass
class RailEnergyParams:
    """All values in SI: joules, watts, seconds. None = no frozen model value loaded.

    PATCH 10 -- BOUNDARY DEFINITIONS.  Every energy term below is an INCREMENT
    ABOVE PLATFORM IDLE over its own interval:

        E_wake   := integral over the wake interval of (i(t) - I_platform_idle) * V
        E_settle := integral over the settle interval of (i(t) - I_platform_idle) * V
        E_BLE    := integral over the transmit interval of (i(t) - I_idle) * V

    Platform idle is charged ONCE, across the full 86400 s, by e_total_rail_joules.
    Defining the terms this way is what makes
        E_total = P_platform_idle * 86400 + E_sched
    exact rather than double-counting idle during wake and settle.
    `hardware/measurement_protocol.md` uses these identical boundaries.
    """
    E_wake: float = PENDING                  # J ABOVE IDLE, deep-sleep exit -> firmware ready
    E_settle: float = PENDING                # J ABOVE IDLE, sensor power-on -> first valid PPG sample
    P_active_increment: float = PENDING      # W, whole-system active MINUS platform idle
    P_platform_idle: float = PENDING         # W, board asleep, sensors shut down
    P_accel_lp: float = PENDING              # W ABOVE IDLE, low-power accel outside bursts
    P_accel_active: float = PENDING          # W ABOVE IDLE, accel during a burst
    E_mcu_eval: float = PENDING              # J ABOVE IDLE per trigger evaluation
    E_BLE: float = PENDING                   # J ABOVE IDLE per daily summary transmission
    E_log_day: float = 0.0                   # J/day ABOVE IDLE, logging outside bursts
    N_tx_per_day: int = 1                    # fixed for every arm; never a variable
    accel_included_in_active_increment: bool = PENDING
    """True if the accelerometer was RUNNING while P_active_increment was measured.
    When True the in-burst accelerometer cost is already inside P_active_increment
    and is NOT added again -- the single most likely double-count in this model."""

    def require(self):
        missing = [k for k, v in self.__dict__.items() if v is PENDING]
        if missing:
            raise RuntimeError(
                "energy model called before measurement. Missing: " + ", ".join(missing) +
                "\nLoad the prospectively frozen modelled-energy parameters via from_json().")


@dataclass
class SupplyArchitecture:
    """Li-Po -> conversion -> board.  Documented, not assumed.

    The AMS1117 on a NodeMCU-32S cannot regulate from a single Li-Po: it needs
    ~1.1 V of dropout and specifies a 10 mA minimum load.  Exactly one of the
    two paths below must be selected, wired and recorded before any battery-day
    figure is quoted.
    """
    path: str = PENDING             # "ldo_direct_3v3" | "boost_5v_then_ams1117"
    eta_conversion: float = PENDING # measured input-to-rail efficiency, 0-1
    cell_capacity_mAh: float = 1000.0
    cell_nominal_V: float = 3.7
    cutoff_V: float = 3.5
    usable_fraction: float = PENDING  # measured fraction of the discharge curve reached

    def usable_energy_J(self) -> float:
        if PENDING in (self.usable_fraction, self.eta_conversion, self.path):
            raise RuntimeError("supply architecture not characterised")
        return (self.cell_capacity_mAh / 1000.0) * 3600.0 * self.cell_nominal_V * self.usable_fraction


# ---- which arms must run activity sensing continuously (option B) ------------
REST_CONDITIONAL_ARMS = {"S3r", "S4", "S6"}
CLOCK_DRIVEN_ARMS = {"S1", "S2", "S3", "S5"}


def e_act_joules(arm: str, n_bursts: int, L_min: int, p: RailEnergyParams,
                 n_eval_per_day: int = 1440) -> float:
    """Option B accounting, chosen on physical grounds and stated in the prereg.

    Clock-driven arms need a rest classification only for the minutes they sample,
    so the accelerometer is co-scheduled with the PPG.  Rest-conditional arms must
    know rest state while the PPG is off, so they pay a low-power accelerometer
    OUTSIDE the bursts plus MCU trigger evaluations.

    PATCH 10: the in-burst accelerometer cost is added only when the accelerometer
    was NOT running during the P_active_increment measurement.  The out-of-burst
    term covers 86400 - T_active seconds, never the full day, so the in-burst
    interval cannot be charged twice.
    """
    p.require()
    t_active = n_bursts * L_min * 60.0
    in_burst = 0.0 if p.accel_included_in_active_increment else t_active * p.P_accel_active
    if arm in REST_CONDITIONAL_ARMS:
        return in_burst + (86400.0 - t_active) * p.P_accel_lp + n_eval_per_day * p.E_mcu_eval
    return in_burst


def e_sched_joules(arm: str, n_bursts: int, L_min: int, p: RailEnergyParams) -> float:
    """Schedule-attributable RAIL-LEVEL energy per day (quantity A)."""
    p.require()
    t_active = n_bursts * L_min * 60.0
    return (n_bursts * (p.E_wake + p.E_settle)
            + t_active * p.P_active_increment
            + e_act_joules(arm, n_bursts, L_min, p)
            + p.N_tx_per_day * p.E_BLE
            + p.E_log_day)


def e_total_rail_joules(arm, n_bursts, L_min, p) -> float:
    """Quantity A.  Platform idle is charged exactly once, over the whole day,
    because every term inside e_sched_joules is an increment above idle."""
    p.require()
    return p.P_platform_idle * 86400.0 + e_sched_joules(arm, n_bursts, L_min, p)


def e_total_input_joules(arm, n_bursts, L_min, p, supply: SupplyArchitecture) -> float:
    """Quantity B: battery-side energy, including conversion losses."""
    return e_total_rail_joules(arm, n_bursts, L_min, p) / supply.eta_conversion


def battery_days(arm, n_bursts, L_min, p, supply: SupplyArchitecture) -> float:
    """Battery life.  NEVER computed from a downstream 3.3 V figure alone."""
    return supply.usable_energy_J() / e_total_input_joules(arm, n_bursts, L_min, p, supply)


def solve_bursts(arm: str, e_target_J: float, L_min: int, p: RailEnergyParams,
                 n_max: int = 144) -> int:
    """Largest integer burst count whose E_sched fits the target."""
    p.require()
    n = 0
    while n + 1 <= n_max and e_sched_joules(arm, n + 1, L_min, p) <= e_target_J:
        n += 1
    return n


def from_json(path: str):
    d = json.load(open(path))
    return RailEnergyParams(**d["rail"]), SupplyArchitecture(**d["supply"])
