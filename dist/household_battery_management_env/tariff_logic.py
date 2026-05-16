from datetime import datetime
from .domain import TariffBlock

from .domain import TariffBlock, EnvironmentConfiguration, ElectricityPrice

def calculate_step_cost(
    grid_kwh: float,
    block: TariffBlock,
    prices: ElectricityPrice,
    config: EnvironmentConfiguration
) -> float:
    """
    Calculates total household cost for a 15-min interval (0.25h).
    """
    duration_hours = 0.25
    power_kw = grid_kwh / duration_hours
    
    # 1. Energy and Network Cost
    idx = block.block_index - 1
    energy_cost = 0.0
    
    if grid_kwh > 0:
        # Import
        energy_cost = grid_kwh * (prices.buy_price_eur_kwh + config.tariff_energy_rates[idx])
        
        # Excess Power Penalty
        if power_kw > config.agreed_power_kw[idx]:
            excess_kw = power_kw - config.agreed_power_kw[idx]
            # Simple MVP penalty: PowerRate * excess (distributed for 15 min)
            energy_cost += excess_kw * config.tariff_power_rates[idx] * (duration_hours / 730) # Monthly rate approx
    else:
        # Export (negative grid_kwh)
        energy_cost = grid_kwh * prices.sell_price_eur_kwh
        
    # 2. Fixed Fee (distributed per 15-min interval in a 30-day month)
    fixed_fee_step = (config.fixed_fee_monthly / (30 * 24 * 4))
    
    total_before_tax = energy_cost + fixed_fee_step
    return total_before_tax * (1 + config.vat_rate)

def get_slovenian_tariff_block(dt: datetime) -> TariffBlock:
    """
    Determines the Slovenian tariff block (1-5) based on time and season.
    High Season: Nov, Dec, Jan, Feb.
    Low Season: Others.
    
    Simplified logic for MVP block determination:
    Blocks depend on work day vs holiday and hour ranges.
    """
    month = dt.month
    is_high_season = month in [11, 12, 1, 2]
    hour = dt.hour
    is_workday = dt.weekday() < 5
    
    # 5-level Slovenian tariff matrix (simplified mapping)
    # This maps the 15-min interval to the specific tariff block index
    if is_high_season:
        if is_workday:
            if 7 <= hour < 14 or 16 <= hour < 20: return TariffBlock(1, True)
            if 6 <= hour < 7 or 14 <= hour < 16 or 20 <= hour < 22: return TariffBlock(2, True)
            return TariffBlock(3, True)
        else:
            if 7 <= hour < 22: return TariffBlock(2, True)
            return TariffBlock(3, True)
    else:
        if is_workday:
            if 7 <= hour < 14 or 16 <= hour < 20: return TariffBlock(2, False)
            if 6 <= hour < 7 or 14 <= hour < 16 or 20 <= hour < 22: return TariffBlock(3, False)
            return TariffBlock(4, False)
        else:
            if 7 <= hour < 22: return TariffBlock(3, False)
            return TariffBlock(4, False)