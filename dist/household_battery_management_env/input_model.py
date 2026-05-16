import numpy as np
from datetime import datetime, timedelta
from typing import List, Tuple
from .domain import WeatherCondition, ForecastSignal, TariffBlock, ElectricityPrice
from .tariff_logic import get_slovenian_tariff_block

class DummyInputModel:
    """Generates deterministic electricity signals for the environment."""
    
    def __init__(self, seed: int = 42, days: int = 7, start_date: datetime = None, pv_peak_kw: float = 1.5):
        self.seed = seed
        self.days = days
        self.start_date = start_date or datetime(2026, 1, 1)
        self.pv_peak_kw = pv_peak_kw
        self.rng = np.random.default_rng(seed)
        
        self.timesteps_per_day = 96  # 15-minute intervals
        self.total_timesteps = self.days * self.timesteps_per_day
        
        self._generate_signals()

    def _generate_signals(self) -> None:
        """Generates the full sequence of signals for the episode duration."""
        # 1. Weather
        weather_pattern = [WeatherCondition.CLEAR, WeatherCondition.CLOUDY, WeatherCondition.RAINY]
        self.daily_weather = [weather_pattern[i % 3] for i in range(self.days)]
        
        # 2. Consumption (kWh per 15 min)
        # Base daily curve: peaks at 8am (32) and 7pm (76)
        x = np.linspace(0, 24, self.timesteps_per_day, endpoint=False)
        base_cons = 0.2 * np.exp(-((x - 8)**2 / 4)) + 0.3 * np.exp(-((x - 19)**2 / 6)) + 0.1
        
        self.consumption = np.tile(base_cons, self.days)
        # Add slight deterministic noise based on seed
        noise = self.rng.uniform(0.9, 1.1, self.total_timesteps)
        self.consumption *= noise
        
        # Scale to 25-35 kWh per day
        for d in range(self.days):
            day_slice = slice(d * 96, (d + 1) * 96)
            daily_sum = np.sum(self.consumption[day_slice])
            # Use the local rng to ensure target_sum is deterministic per seed
            target_sum = 25.0 + (self.rng.random() * 10.0)
            if daily_sum > 0:
                self.consumption[day_slice] *= (target_sum / daily_sum)

        # 3. PV Production (kWh per 15 min)
        weather_factors = {
            WeatherCondition.CLEAR: 1.0,
            WeatherCondition.CLOUDY: 0.4,
            WeatherCondition.RAINY: 0.1
        }
        
        self.pv_production = np.zeros(self.total_timesteps)
        for d in range(self.days):
            factor = weather_factors[self.daily_weather[d]]
            # Solar peak at noon (48)
            day_x = np.linspace(0, 24, self.timesteps_per_day, endpoint=False)
            # Sine wave between 6am (24) and 6pm (72)
            # Peak power is defined at solar noon, scaled by weather factor
            solar_curve = np.maximum(0, np.sin(np.pi * (day_x - 6) / 12)) * (self.pv_peak_kw / 4.0) * factor
            self.pv_production[d * 96 : (d + 1) * 96] = solar_curve

        # 4. Tariff Blocks
        self.tariff_blocks = []
        for t in range(self.total_timesteps):
            current_dt = self.start_date + timedelta(minutes=t * 15)
            self.tariff_blocks.append(get_slovenian_tariff_block(current_dt))

    def get_step_data(self, step_index: int) -> Tuple[float, float, TariffBlock, ForecastSignal, ElectricityPrice]:
        """Returns data for a specific timestep."""
        if step_index >= self.total_timesteps:
            raise IndexError(f"Step index {step_index} out of bounds for {self.total_timesteps} steps.")
            
        cons = self.consumption[step_index]
        pv = self.pv_production[step_index]
        block = self.tariff_blocks[step_index]
        prices = ElectricityPrice(buy_price_eur_kwh=0.15, sell_price_eur_kwh=0.05)
        
        # Forecast: next 4 steps
        f_cons = []
        f_pv = []
        for i in range(1, 5):
            idx = step_index + i
            if idx < self.total_timesteps:
                f_cons.append(self.consumption[idx])
                f_pv.append(self.pv_production[idx])
            else:
                f_cons.append(0.0)
                f_pv.append(0.0)
                
        forecast = ForecastSignal(f_cons, f_pv)
        return cons, pv, block, forecast, prices