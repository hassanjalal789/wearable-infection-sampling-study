"""Energy-model unit tests use SYNTHETIC FIXTURE constants, never study values.
The study's constants stay PENDING until bench measurement."""
import pytest
import energy_model as em

FIXTURE = em.RailEnergyParams(
    E_wake=0.060, E_settle=0.040, P_active_increment=0.0120,
    P_platform_idle=0.0155, P_accel_lp=0.00023, P_accel_active=0.0017,
    E_mcu_eval=0.000020, E_BLE=0.0013, E_log_day=0.5, N_tx_per_day=1,
    accel_included_in_active_increment=True)
SUPPLY = em.SupplyArchitecture(path="ldo_direct_3v3", eta_conversion=0.88,
                               usable_fraction=0.85)


def test_model_refuses_to_run_before_measurement():
    with pytest.raises(RuntimeError, match="before measurement"):
        em.e_sched_joules("S3", 7, 10, em.RailEnergyParams())


def test_supply_refuses_before_characterisation():
    with pytest.raises(RuntimeError, match="not characterised"):
        em.SupplyArchitecture().usable_energy_J()


def test_rest_conditional_arms_pay_more_activity_energy():
    a = em.e_act_joules("S3", 7, 10, FIXTURE)     # clock-driven
    b = em.e_act_joules("S6", 7, 10, FIXTURE)     # rest-conditional
    assert b > a


def test_solver_is_maximal_and_within_budget():
    target = em.e_sched_joules("S3", 7, 10, FIXTURE)
    n = em.solve_bursts("S3", target, 10, FIXTURE)
    assert n == 7
    assert em.e_sched_joules("S3", n, 10, FIXTURE) <= target
    assert em.e_sched_joules("S3", n + 1, 10, FIXTURE) > target


def test_matched_arms_land_within_five_percent():
    target = em.e_sched_joules("S2", 8, 10, FIXTURE)
    for arm in ("S2", "S3", "S5"):
        n = em.solve_bursts(arm, target, 10, FIXTURE)
        e = em.e_sched_joules(arm, n, 10, FIXTURE)
        assert abs(e - target) / target <= 0.05, (arm, e, target)


def test_battery_days_use_input_side_energy_not_rail():
    rail = em.e_total_rail_joules("S3", 7, 10, FIXTURE)
    inp = em.e_total_input_joules("S3", 7, 10, FIXTURE, SUPPLY)
    assert inp > rail                                   # conversion losses included
    assert em.battery_days("S3", 7, 10, FIXTURE, SUPPLY) < SUPPLY.usable_energy_J() / rail
