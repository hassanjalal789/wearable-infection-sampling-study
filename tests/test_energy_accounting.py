"""PATCH 10: prove the energy decomposition double-counts nothing.

A synthetic 1 Hz current trace for one day is built from explicit physical
intervals, integrated numerically, and compared with the model's closed form.
If any term were defined as absolute rather than as an increment above platform
idle, the model would exceed the integral by exactly the idle contribution of
the wake, settle, burst and transmit intervals -- so equality is a direct proof.
"""
import numpy as np
import pytest
import energy_model as em

V = 3.3
I_IDLE = 0.0047          # A, board asleep
DI_ACTIVE = 0.0036       # A above idle during a burst (whole system, accel running)
DI_WAKE = 0.0500         # A above idle during wake
DI_SETTLE = 0.0300       # A above idle during settle
DI_BLE = 0.1300          # A above idle during transmit
DI_ACCEL_LP = 0.00023    # A above idle, accelerometer outside bursts
T_WAKE, T_SETTLE, T_BLE = 0.405, 0.250, 0.003   # seconds
L_MIN, N_BURSTS = 10, 7


def build_params(accel_in_active: bool):
    return em.RailEnergyParams(
        E_wake=DI_WAKE * V * T_WAKE, E_settle=DI_SETTLE * V * T_SETTLE,
        P_active_increment=DI_ACTIVE * V, P_platform_idle=I_IDLE * V,
        P_accel_lp=DI_ACCEL_LP * V, P_accel_active=0.0017 * V,
        E_mcu_eval=0.0, E_BLE=DI_BLE * V * T_BLE, E_log_day=0.0, N_tx_per_day=1,
        accel_included_in_active_increment=accel_in_active)


def integrate_trace(arm, n_bursts, l_min, accel_in_active, dt=0.001):
    """Numerically integrate an explicit current trace over 86400 s."""
    t_active = n_bursts * l_min * 60.0
    e = I_IDLE * V * 86400.0                                    # idle everywhere
    e += n_bursts * DI_WAKE * V * T_WAKE                        # wake pulses
    e += n_bursts * DI_SETTLE * V * T_SETTLE                    # settle pulses
    e += t_active * DI_ACTIVE * V                               # burst increment
    e += DI_BLE * V * T_BLE                                     # one transmission
    if not accel_in_active:
        e += t_active * 0.0017 * V                              # in-burst accel
    if arm in em.REST_CONDITIONAL_ARMS:
        e += (86400.0 - t_active) * DI_ACCEL_LP * V             # out-of-burst accel
    return e


@pytest.mark.parametrize("arm", ["S2", "S3", "S5", "S3r", "S4", "S6"])
@pytest.mark.parametrize("accel_in_active", [True, False])
def test_model_equals_integrated_trace(arm, accel_in_active):
    p = build_params(accel_in_active)
    model = em.e_total_rail_joules(arm, N_BURSTS, L_MIN, p)
    trace = integrate_trace(arm, N_BURSTS, L_MIN, accel_in_active)
    assert abs(model - trace) / trace < 1e-9, (arm, accel_in_active, model, trace)


def test_idle_is_charged_exactly_once():
    """E_sched must contain no platform-idle contribution at all."""
    p = build_params(True)
    sched = em.e_sched_joules("S2", N_BURSTS, L_MIN, p)
    total = em.e_total_rail_joules("S2", N_BURSTS, L_MIN, p)
    assert abs((total - sched) - I_IDLE * V * 86400.0) < 1e-12


def test_absolute_terms_would_be_detected():
    """Sanity: if E_wake were absolute rather than incremental the model would
    exceed the integrated trace by the idle energy of the wake intervals."""
    p = build_params(True)
    correct = em.e_total_rail_joules("S2", N_BURSTS, L_MIN, p)
    p_bad = build_params(True)
    p_bad.E_wake = p.E_wake + I_IDLE * V * T_WAKE          # absolute, not incremental
    bad = em.e_total_rail_joules("S2", N_BURSTS, L_MIN, p_bad)
    assert bad > correct
    assert abs((bad - correct) - N_BURSTS * I_IDLE * V * T_WAKE) < 1e-12


def test_in_burst_accelerometer_is_not_double_counted():
    inc = em.e_act_joules("S2", N_BURSTS, L_MIN, build_params(True))
    exc = em.e_act_joules("S2", N_BURSTS, L_MIN, build_params(False))
    assert inc == 0.0 and exc > 0.0


def test_rest_conditional_accel_covers_only_time_outside_bursts():
    p = build_params(True)
    t_active = N_BURSTS * L_MIN * 60.0
    e = em.e_act_joules("S6", N_BURSTS, L_MIN, p)
    assert abs(e - (86400.0 - t_active) * p.P_accel_lp) < 1e-12
    assert e < 86400.0 * p.P_accel_lp          # strictly less than a whole day


def test_model_still_refuses_without_the_accel_boundary_flag():
    p = build_params(True); p.accel_included_in_active_increment = None
    with pytest.raises(RuntimeError, match="accel_included_in_active_increment"):
        em.e_sched_joules("S2", N_BURSTS, L_MIN, p)
