import pytest
import numpy as np
from household_battery_management_env.domain import Battery, EnvironmentConfiguration, BatteryAction
from household_battery_management_env.envs import BatteryManagementEnvironment

def make_env(seed=42):
    bat = Battery(
        capacity_kwh=10.0,
        current_charge_kwh=5.0,
        min_charge_kwh=1.0,
        max_charge_kwh=9.0,
        charge_rate_kw=2.0,
        discharge_rate_kw=2.0
    )
    config = EnvironmentConfiguration(battery=bat, seed=seed, days=1)
    return BatteryManagementEnvironment(config)

def run_episode(env, actions):
    history = []
    obs, info = env.reset()
    history.append((obs, info))
    
    for action in actions:
        obs, reward, term, trunc, info = env.step(action)
        history.append((obs, reward, term, trunc, info))
        if term or trunc:
            break
    return history

def test_environment_absolute_determinism():
    """
    Verify that two separate environment instances with the same seed
    and same action sequence produce identical outputs.
    """
    seed = 12345
    actions = [BatteryAction.CHARGE, BatteryAction.HOLD, BatteryAction.DISCHARGE] * 10
    
    env1 = make_env(seed)
    env2 = make_env(seed)
    
    hist1 = run_episode(env1, actions)
    hist2 = run_episode(env2, actions)
    
    assert len(hist1) == len(hist2)
    
    for i, (step1, step2) in enumerate(zip(hist1, hist2)):
        # Step 0 is (obs, info) from reset
        if i == 0:
            np.testing.assert_array_equal(step1[0], step2[0], err_msg=f"Observation mismatch at reset")
            assert step1[1] == step2[1], f"Info mismatch at reset"
        else:
            # Step result: (obs, reward, term, trunc, info)
            np.testing.assert_array_equal(step1[0], step2[0], err_msg=f"Observation mismatch at step {i}")
            assert step1[1] == step2[1], f"Reward mismatch at step {i}"
            assert step1[2] == step2[2], f"Terminated mismatch at step {i}"
            assert step1[3] == step2[3], f"Truncated mismatch at step {i}"
            assert step1[4] == step2[4], f"Info mismatch at step {i}"

def test_determinism_after_reset():
    """Verify that calling reset() on the same instance restores determinism."""
    env = make_env(seed=99)
    actions = [BatteryAction.CHARGE] * 5
    
    hist1 = run_episode(env, actions)
    hist2 = run_episode(env, actions) # Second run on same instance
    
    for i in range(len(hist1)):
        # Compare observations
        np.testing.assert_array_equal(hist1[i][0], hist2[i][0])
        # Compare rewards (from index 1 onwards)
        if i > 0:
            assert hist1[i][1] == hist2[i][1]

def test_different_seeds_produce_different_results():
    """Sanity check: different seeds should NOT produce identical outputs."""
    env1 = make_env(seed=1)
    env2 = make_env(seed=2)
    
    obs1, _ = env1.reset()
    obs2, _ = env2.reset()
    
    # It is statistically highly unlikely for observations to be identical
    assert not np.array_equal(obs1, obs2)