from dataclasses import dataclass, field
from typing import List, Tuple
from .domain import BatteryAction, WeatherCondition

@dataclass
class Particle:
    """A visual particle for energy flow animation."""
    pos: List[float] # [x, y]
    target: Tuple[float, float]
    speed: float
    color: Tuple[int, int, int]
    size: int

@dataclass
class VisualState:
    """Tracks state for smoothing and animations."""
    battery_charge_pct: float = 0.0
    cons_kwh: float = 0.0
    pv_kwh: float = 0.0
    reward_history: List[float] = field(default_factory=list)
    cost_history: List[float] = field(default_factory=list)
    particles: List[Particle] = field(default_factory=list)
    active_callouts: List[dict] = field(default_factory=list) # {text, pos, ttl}
    weather: WeatherCondition = WeatherCondition.CLEAR
    time_of_day: float = 0.0 # 0.0 to 24.0