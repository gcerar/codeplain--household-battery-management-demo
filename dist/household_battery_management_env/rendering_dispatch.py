import numpy as np
from typing import Optional, Any, Dict, Tuple
from .domain import BatteryAction
from .utils import render_env_state

def dispatch_render(
    render_mode: Optional[str],
    current_step: int,
    total_timesteps: int,
    battery: Any,
    last_reward: float,
    model: Any,
    viewer: Any,
    last_grid_kwh: float,
    last_action: int,
    last_cost: float
) -> Tuple[Optional[str], Any]:
    """
    Dispatches rendering to the appropriate backend and manages the viewer instance.
    
    Returns:
        Tuple[Optional[str], Any]: (render_output, updated_viewer)
    """
    if render_mode == "ansi":
        return render_env_state(
            render_mode,
            current_step,
            total_timesteps,
            battery.current_charge_kwh,
            last_reward,
            model
        ), viewer

    if render_mode is None:
        return None, viewer

    # Prepare visual state for graphical renders
    # Clamp step for data retrieval if at terminal state
    data_step = min(current_step, total_timesteps - 1)
    cons, pv, block, _, _ = model.get_step_data(data_step)
    
    state_info = {
        "charge_pct": battery.current_charge_kwh / battery.max_charge_kwh,
        "hour": (current_step % 96) / 4.0,
        "pv": pv,
        "cons": cons,
        "grid_kwh": last_grid_kwh,
        "reward": last_reward,
        "action": BatteryAction(last_action),
        "block": block.block_index,
        "weather": model.daily_weather[current_step // 96],
        "cost": last_cost
    }

    if render_mode == "matplotlib":
        if viewer is None:
            from .rendering_mpl import LiveRenderWindow
            viewer = LiveRenderWindow()
        viewer.update(battery.current_charge_kwh, last_reward, current_step)
        
    elif render_mode == "human":
        if viewer is None:
            from .rendering_pygame import ShowcaseRenderWindow
            viewer = ShowcaseRenderWindow()
        viewer.update(state_info)
    
    return None, viewer