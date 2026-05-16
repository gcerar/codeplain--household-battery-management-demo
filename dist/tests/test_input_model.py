import pytest
from datetime import datetime
from household_battery_management_env.input_model import DummyInputModel
from household_battery_management_env.domain import WeatherCondition

def test_dummy_model_determinism():
    """Ensure same seed produces same output."""
    m1 = DummyInputModel(seed=100, days=1)
    m2 = DummyInputModel(seed=100, days=1)
    
    c1, p1, _, _, _ = m1.get_step_data(10)
    c2, p2, _, _, _ = m2.get_step_data(10)
    
    assert c1 == c2
    assert p1 == p2

def test_consumption_daily_limits():
    """Verify daily consumption is within 25-35 kWh."""
    days = 3
    model = DummyInputModel(seed=42, days=days)
    
    for d in range(days):
        daily_sum = sum(model.consumption[d*96 : (d+1)*96])
        assert 25.0 <= daily_sum <= 35.0

def test_pv_night_production():
    """Solar production should be zero at night (e.g., 00:00 to 05:00)."""
    model = DummyInputModel(days=1)
    # Check first 20 intervals (00:00 to 05:00)
    for i in range(20):
        _, pv, _, _, _ = model.get_step_data(i)
        assert pv == 0.0

def test_forecast_signal_behavior():
    """Check forecast values and boundary conditions."""
    model = DummyInputModel(days=1)
    total_steps = 96
    
    # Near end of episode
    _, _, _, forecast, _ = model.get_step_data(total_steps - 2)
    # Last 2 of 4 forecast steps should be 0
    assert len(forecast.consumption_forecast) == 4
    assert forecast.consumption_forecast[2] == 0.0
    assert forecast.consumption_forecast[3] == 0.0

def test_weather_pattern():
    """Verify deterministic weather rotation."""
    model = DummyInputModel(days=4)
    assert model.daily_weather[0] == WeatherCondition.CLEAR
    assert model.daily_weather[1] == WeatherCondition.CLOUDY
    assert model.daily_weather[2] == WeatherCondition.RAINY
    assert model.daily_weather[3] == WeatherCondition.CLEAR