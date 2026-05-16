from typing import Tuple
from .domain import Battery, BatteryAction, EnvironmentConfiguration, ElectricityPrice, TariffBlock
from .tariff_logic import calculate_step_cost

def apply_battery_physics(
    battery: Battery, 
    action: int, 
    dt: float = 0.25
) -> float:
    """
    Applies battery charging/discharging physics and returns net energy flow.
    
    Args:
        battery: The battery object to mutate.
        action: The BatteryAction to perform.
        dt: Time delta in hours (default 0.25 for 15 mins).
        
    Returns:
        float: net_energy (positive for discharge to house, negative for charge from house).
    """
    net_energy = 0.0
    if action == BatteryAction.CHARGE:
        max_charge = min(
            battery.charge_rate_kw * dt, 
            battery.max_charge_kwh - battery.current_charge_kwh
        )
        battery.current_charge_kwh += max_charge
        net_energy = -max_charge
    elif action == BatteryAction.DISCHARGE:
        max_discharge = min(
            battery.discharge_rate_kw * dt, 
            battery.current_charge_kwh - battery.min_charge_kwh
        )
        battery.current_charge_kwh -= max_discharge
        net_energy = max_discharge
    return net_energy

def calculate_step_results(
    battery: Battery,
    action: int,
    cons: float,
    pv: float,
    block: TariffBlock,
    prices: ElectricityPrice,
    config: EnvironmentConfiguration
) -> Tuple[float, float, float, float]:
    """
    Calculates grid flow, cost, penalty, and reward for a step.
    
    Returns:
        Tuple: (grid_kwh, cost, penalty, reward)
    """
    net_energy = apply_battery_physics(battery, action)
    
    # Net grid = Consumption - PV - (Battery Energy Flow)
    grid_kwh = cons - pv - net_energy
    
    cost = calculate_step_cost(grid_kwh, block, prices, config)
    
    # Apply penalty for clipping/invalid physics
    penalty = 0.0
    if action == BatteryAction.CHARGE and battery.current_charge_kwh >= battery.max_charge_kwh:
        penalty = 0.5
    elif action == BatteryAction.DISCHARGE and battery.current_charge_kwh <= battery.min_charge_kwh:
        penalty = 0.5
        
    reward = -(cost + penalty)
    return grid_kwh, cost, penalty, float(reward)