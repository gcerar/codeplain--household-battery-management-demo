import pytest
import numpy as np
from household_battery_management_env.domain import Battery, EnvironmentConfiguration
from household_battery_management_env.envs import BatteryManagementEnvironment

def test_render_modes_available():
    bat = Battery(10, 5, 0, 10, 5, 5)
    config = EnvironmentConfiguration(battery=bat)
    env = BatteryManagementEnvironment(config)
    assert "human" in env.metadata["render_modes"]
    assert "matplotlib" in env.metadata["render_modes"]
    assert "ansi" in env.metadata["render_modes"]

def test_ansi_render_output():
    bat = Battery(10, 5, 0, 10, 5, 5)
    config = EnvironmentConfiguration(battery=bat)
    env = BatteryManagementEnvironment(config, render_mode="ansi")
    env.reset()
    output = env.render()
    assert isinstance(output, str)
    assert "Battery:" in output
    assert "Time:" in output

@pytest.mark.skip(reason="Requires graphical display")
def test_human_render_init():
    bat = Battery(10, 5, 0, 10, 5, 5)
    config = EnvironmentConfiguration(battery=bat)
    env = BatteryManagementEnvironment(config, render_mode="human")
    env.reset()
    env.render() # Should initialize Pygame
    assert env._viewer is not None