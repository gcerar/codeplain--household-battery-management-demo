import pytest
import numpy as np
from household_battery_management_env.domain import Battery, EnvironmentConfiguration, BatteryAction
from household_battery_management_env.envs import BatteryManagementEnvironment

@pytest.fixture
def env_config():
    bat = Battery(
        capacity_kwh=10.0,
        current_charge_kwh=2.0,
        min_charge_kwh=2.0,
        max_charge_kwh=10.0,
        charge_rate_kw=5.0,
        discharge_rate_kw=5.0
    )
    return EnvironmentConfiguration(battery=bat, days=1, seed=42)

def test_env_reset(env_config):
    env = BatteryManagementEnvironment(env_config)
    obs, info = env.reset()
    
    assert len(obs) == 12
    assert "tariff_block" in info
    assert obs[0] == env_config.battery.current_charge_kwh

def test_env_step_charge(env_config):
    env = BatteryManagementEnvironment(env_config)
    env.reset()
    
    # Charge action
    obs, reward, terminated, truncated, info = env.step(BatteryAction.CHARGE)
    
    # 5kW * 0.25h = 1.25kWh charge
    assert obs[0] == 2.0 + 1.25
    assert not terminated

def test_env_step_invalid_action(env_config):
    env = BatteryManagementEnvironment(env_config)
    env.reset()
    with pytest.raises(ValueError, match="Invalid action"):
        env.step(99)

def test_env_termination(env_config):
    env = BatteryManagementEnvironment(env_config)
    env.reset()
    
    # Run for 96 steps (1 day)
    for _ in range(95):
        _, _, term, _, _ = env.step(BatteryAction.HOLD)
        assert not term
        
    _, _, term, _, _ = env.step(BatteryAction.HOLD)
    assert term

def test_env_step_penalty_and_clipping(env_config):
    # Setup battery at max charge
    env_config.battery.current_charge_kwh = env_config.battery.max_charge_kwh
    env = BatteryManagementEnvironment(env_config)
    env.reset()
    
    # Force charge at max capacity
    obs, reward, terminated, truncated, info = env.step(BatteryAction.CHARGE)
    
    # Charge should be clipped (no change)
    assert obs[0] == env_config.battery.max_charge_kwh
    # Penalty should be present in info and reflected in reward
    assert info["penalty"] > 0
    assert reward < -info["cost"]

def test_env_step_terminal_info(env_config):
    env = BatteryManagementEnvironment(env_config)
    env.reset()
    
    # Run until the last step
    for _ in range(95):
        env.step(BatteryAction.HOLD)
    
    obs, reward, terminated, truncated, info = env.step(BatteryAction.HOLD)
    assert terminated
    assert "terminal_observation" in info
    assert isinstance(info["terminal_observation"], np.ndarray)

def test_env_render_ansi(env_config):
    env = BatteryManagementEnvironment(env_config)
    env.render_mode = "ansi"
    env.reset()
    
    # Check render after reset
    render_output = env.render()
    assert isinstance(render_output, str)
    assert "Time:" in render_output
    assert "Battery:" in render_output
    assert "Cons:" in render_output
    assert "PV:" in render_output
    assert "Tariff Block:" in render_output
    assert "Last Reward:" in render_output

    # Check render after step
    env.step(BatteryAction.CHARGE)
    render_output_post_step = env.render()
    assert "Last Reward:" in render_output_post_step
    # Verify values are present (basic check for non-empty/non-zero formatting)
    assert "kWh" in render_output_post_step