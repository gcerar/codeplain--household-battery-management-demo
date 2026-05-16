import gymnasium as gym
import numpy as np
from gymnasium import spaces
from typing import Any, Dict, Tuple, Optional

from .domain import (
    BatteryAction, 
    EnvironmentConfiguration, 
    Battery
)
from .validation import validate_config
from .input_model import DummyInputModel
from .physics import calculate_step_results
from .utils import format_observation
from .rendering_dispatch import dispatch_render

class BatteryManagementEnvironment(gym.Env):
    """
    Gymnasium environment for managing a household battery.
    Targeted at DRL researchers and ML engineers.
    """
    metadata = {"render_modes": ["human", "ansi", "matplotlib"]}

    def __init__(self, config: EnvironmentConfiguration, render_mode: Optional[str] = None):
        super().__init__()
        self.config = validate_config(config)
        self.render_mode = render_mode
        self.last_reward = 0.0
        self.model = DummyInputModel(seed=config.seed, days=config.days, pv_peak_kw=config.pv_peak_kw)
        
        # Create a local copy of battery state to avoid mutating the config object
        orig = config.battery
        self.battery = Battery(
            capacity_kwh=orig.capacity_kwh,
            current_charge_kwh=orig.current_charge_kwh,
            min_charge_kwh=orig.min_charge_kwh,
            max_charge_kwh=orig.max_charge_kwh,
            charge_rate_kw=orig.charge_rate_kw,
            discharge_rate_kw=orig.discharge_rate_kw
        )
        
        # Action space: 0=Hold, 1=Charge, 2=Discharge
        self.action_space = spaces.Discrete(3)
        
        # Observation space: 
        # [charge, hour, consumption, pv, 4_cons_forecast, 4_pv_forecast]
        self.observation_space = spaces.Box(
            low=0, 
            high=np.inf, 
            shape=(12,), 
            dtype=np.float32
        )
        
        self.current_step = 0
        self._viewer = None

    def reset(self, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Resets the environment to the initial state.
        
        Args:
            seed: The seed that is used to initialize the environment's PRNG.
            options: Additional information to specify how the environment is reset.

        Returns:
            The initial observation and info dictionary.
        """
        super().reset(seed=seed)
        
        # If a seed is provided, we must re-initialize the dummy model to ensure determinism.
        # This aligns with Gymnasium's requirement that reset(seed=...) forces determinism.
        if seed is not None:
            self.model = DummyInputModel(seed=seed, days=self.config.days, pv_peak_kw=self.config.pv_peak_kw)
        elif self.current_step > 0:
            # Re-initialize even if seed is None to reset the internal RNG state of the model
            self.model = DummyInputModel(seed=self.config.seed, days=self.config.days, pv_peak_kw=self.config.pv_peak_kw)
        
        self.current_step = 0
        # Reset battery charge to the initial configuration value
        self.battery.current_charge_kwh = self.config.battery.current_charge_kwh
        
        # Retrieve the first timestep data from the model
        cons, pv, block, forecast, _ = self.model.get_step_data(self.current_step)
        observation = format_observation(self.battery, self.current_step, cons, pv, forecast)
        
        info = {
            "tariff_block": block.block_index,
            "step": self.current_step,
            "weather": self.model.daily_weather[0].value
        }
        
        return observation, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        if not self.action_space.contains(action):
            error_msg = (
                f"Invalid action {action} provided to step(). "
                f"Action must be an integer in the range [0, 2] (Hold, Charge, Discharge). "
                f"Check your DRL agent's output layer or action selection logic."
            )
            raise ValueError(error_msg)

        # 1. Get current environment data
        cons, pv, block, forecast, prices = self.model.get_step_data(self.current_step)
        
        # 2. Apply Physics and calculate Reward/Cost
        grid_kwh, cost, penalty, reward = calculate_step_results(
            self.battery, action, cons, pv, block, prices, self.config
        )
        
        self._last_grid_kwh = grid_kwh
        self._last_action = action
        self._last_cost = cost
        self.last_reward = reward
        
        # 4. Advance Step
        self.current_step += 1
        terminated = self.current_step >= self.model.total_timesteps
        truncated = False
        
        if not terminated:
            next_cons, next_pv, next_block, next_forecast, _ = self.model.get_step_data(self.current_step)
            obs = format_observation(self.battery, self.current_step, next_cons, next_pv, next_forecast)
            info = {
                "tariff_block": next_block.block_index, 
                "cost": cost, 
                "grid_kwh": grid_kwh,
                "penalty": penalty
            }
        else:
            # Gymnasium standard: return the last observation, but often wrappers 
            # expect terminal observation in info.
            obs = format_observation(self.battery, self.current_step - 1, cons, pv, forecast)
            info = {
                "tariff_block": block.block_index, 
                "cost": cost, 
                "grid_kwh": grid_kwh,
                "penalty": penalty,
                "terminal_observation": obs
            }

        return obs, float(reward), terminated, truncated, info

    def render(self) -> Optional[str]:
        """
        Renders the environment state.
        """
        output, self._viewer = dispatch_render(
            render_mode=self.render_mode,
            current_step=self.current_step,
            total_timesteps=self.model.total_timesteps,
            battery=self.battery,
            last_reward=self.last_reward,
            model=self.model,
            viewer=self._viewer,
            last_grid_kwh=getattr(self, '_last_grid_kwh', 0.0),
            last_action=getattr(self, '_last_action', BatteryAction.HOLD),
            last_cost=getattr(self, '_last_cost', 0.0)
        )
        return output