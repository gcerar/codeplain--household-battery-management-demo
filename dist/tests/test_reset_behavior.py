import pytest
import numpy as np
from household_battery_management_env.domain import Battery, EnvironmentConfiguration
from household_battery_management_env.envs import BatteryManagementEnvironment

@pytest.fixture
def basic_config():
    bat = Battery(
        capacity_kwh=10.0,
        current_charge_kwh=5.0, # Start at 5.0
        min_charge_kwh=2.0,      # reset should go here
        max_charge_kwh=10.0,
        charge_rate_kw=5.0,
        discharge_rate_kw=5.0
    )
    return EnvironmentConfiguration(battery=bat, days=1, seed=42)

def test_reset_initializes_battery_charge(basic_config):
    """Test that reset sets the battery charge back to the initial configuration value."""
    initial_charge = basic_config.battery.current_charge_kwh
    env = BatteryManagementEnvironment(basic_config)
    
    # Manually change charge in the environment
    env.battery.current_charge_kwh = 8.0
    
    obs, info = env.reset()
    
    # Check battery charge in observation (index 0) and object matches initial config
    assert env.battery.current_charge_kwh == initial_charge
    assert obs[0] == initial_charge

def test_reset_returns_correct_types(basic_config):
    """Test that reset returns the expected Gymnasium types."""
    env = BatteryManagementEnvironment(basic_config)
    obs, info = env.reset()
    
    assert isinstance(obs, np.ndarray)
    assert obs.dtype == np.float32
    assert isinstance(info, dict)
    assert "tariff_block" in info
    assert "step" in info

def test_reset_with_seed_is_deterministic(basic_config):
    """Test that reset with a specific seed produces consistent initial observations."""
    env = BatteryManagementEnvironment(basic_config)
    
    obs1, _ = env.reset(seed=123)
    obs2, _ = env.reset(seed=123)
    obs3, _ = env.reset(seed=456)
    
    np.testing.assert_array_equal(obs1, obs2)
    with pytest.raises(AssertionError):
        np.testing.assert_array_equal(obs1, obs3)

def test_reset_starts_at_step_zero(basic_config):
    """Test that reset starts at the beginning of the dummy model data."""
    env = BatteryManagementEnvironment(basic_config)
    env.step(0) # Advance
    assert env.current_step == 1
    
    env.reset()
    assert env.current_step == 0
    
    # Check that 'hour' in observation (index 1) is 0.0
    obs, _ = env.reset()
    assert obs[1] == 0.0