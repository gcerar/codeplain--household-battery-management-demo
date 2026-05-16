import numpy as np
from typing import Optional
from .domain import ForecastSignal, Battery

def format_observation(
    battery: Battery, 
    current_step: int, 
    cons: float, 
    pv: float, 
    forecast: ForecastSignal
) -> np.ndarray:
    """
    Formats the environment state into a flat numpy array for the observation space.
    """
    hour = (current_step % 96) / 4.0
    return np.array([
        battery.current_charge_kwh,
        hour,
        cons,
        pv,
        *forecast.consumption_forecast,
        *forecast.pv_forecast
    ], dtype=np.float32)

def render_env_state(
    render_mode: Optional[str],
    current_step: int,
    total_timesteps: int,
    battery_charge: float,
    last_reward: float,
    model: any
) -> Optional[str]:
    """
    Generates a string representation of the environment state for ANSI rendering.
    """
    if render_mode != "ansi":
        return None
        
    # Handle edge case where current_step might be at total_timesteps after an episode
    step_to_show = min(current_step, total_timesteps - 1)
    try:
        cons, pv, block, _, _ = model.get_step_data(step_to_show)
    except (IndexError, AttributeError) as e:
        return f"Error retrieving render data: {str(e)}"
        
    hour = (step_to_show % 96) / 4.0
    
    return (
        f"Time: {hour:05.2f}h | "
        f"Battery: {battery_charge:.2f} kWh | "
        f"Cons: {cons:.3f} kWh | "
        f"PV: {pv:.3f} kWh | "
        f"Tariff Block: {block.block_index} | "
        f"Last Reward: {last_reward:.4f}"
    )