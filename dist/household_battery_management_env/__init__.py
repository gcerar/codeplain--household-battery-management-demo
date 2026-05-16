from gymnasium.envs.registration import register
from .domain import Battery, EnvironmentConfiguration, BatteryAction
from .envs import BatteryManagementEnvironment

register(
    id="household_battery_management_env/BatteryMgmt-v0",
    entry_point="household_battery_management_env.envs:BatteryManagementEnvironment",
)

__all__ = ["BatteryManagementEnvironment", "Battery", "EnvironmentConfiguration", "BatteryAction"]