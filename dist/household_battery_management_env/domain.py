from dataclasses import dataclass, field
from enum import IntEnum, Enum
from typing import List

class BatteryAction(IntEnum):
    """Discrete actions for the battery management."""
    HOLD = 0
    CHARGE = 1
    DISCHARGE = 2

class WeatherCondition(Enum):
    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAINY = "rainy"

@dataclass(frozen=True)
class ForecastSignal:
    """Next four timesteps of consumption and PV production."""
    consumption_forecast: List[float]  # kWh
    pv_forecast: List[float]           # kWh

@dataclass(frozen=True)
class TariffBlock:
    """Represents a Slovenian 5-level tariff block (1-5)."""
    block_index: int  # 1 to 5
    is_high_season: bool

@dataclass
class Battery:
    """Represents the physical battery storage."""
    capacity_kwh: float
    current_charge_kwh: float
    min_charge_kwh: float
    max_charge_kwh: float
    charge_rate_kw: float
    discharge_rate_kw: float

@dataclass(frozen=True)
class ElectricityPrice:
    """Buy and sell prices for electricity."""
    buy_price_eur_kwh: float
    sell_price_eur_kwh: float

@dataclass(frozen=True)
class EnvironmentConfiguration:
    """Configuration for the BatteryManagementEnvironment."""
    battery: Battery
    days: int = 7
    seed: int = 42
    vat_rate: float = 0.22
    fixed_fee_monthly: float = 5.0
    pv_peak_kw: float = 10.0
    # Slovenian Tariff Rates (EUR/kWh and EUR/kW)
    # Indices 0-4 correspond to Blocks 1-5
    tariff_energy_rates: List[float] = field(default_factory=lambda: [0.02, 0.018, 0.015, 0.012, 0.01])
    tariff_power_rates: List[float] = field(default_factory=lambda: [3.5, 3.0, 2.5, 2.0, 1.5])
    agreed_power_kw: List[float] = field(default_factory=lambda: [5.0, 5.0, 5.0, 5.0, 5.0])