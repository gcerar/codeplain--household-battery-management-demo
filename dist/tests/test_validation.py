import pytest
from household_battery_management_env.domain import Battery, EnvironmentConfiguration
from household_battery_management_env.validation import validate_config

def test_validation_coerces_charge_bounds():
    bat = Battery(
        capacity_kwh=10.0,
        current_charge_kwh=15.0, # Too high
        min_charge_kwh=2.0,
        max_charge_kwh=8.0,
        charge_rate_kw=5.0,
        discharge_rate_kw=5.0
    )
    config = EnvironmentConfiguration(battery=bat)
    validated = validate_config(config)
    assert validated.battery.current_charge_kwh == 8.0

def test_validation_rejects_invalid_tariff_length():
    bat = Battery(10, 5, 0, 10, 5, 5)
    config = EnvironmentConfiguration(battery=bat, tariff_energy_rates=[0.1, 0.2]) # Only 2
    with pytest.raises(ValueError, match="requires exactly 5 entries"):
        validate_config(config)

def test_validation_rejects_negative_days():
    bat = Battery(10, 5, 0, 10, 5, 5)
    config = EnvironmentConfiguration(battery=bat, days=-1)
    with pytest.raises(ValueError, match="Simulation days must be at least 1"):
        validate_config(config)

def test_validation_rejects_inverted_battery_limits():
    bat = Battery(
        capacity_kwh=10.0,
        current_charge_kwh=5.0,
        min_charge_kwh=8.0,
        max_charge_kwh=2.0, # Min > Max
        charge_rate_kw=5.0,
        discharge_rate_kw=5.0
    )
    config = EnvironmentConfiguration(battery=bat)
    with pytest.raises(ValueError, match="cannot be greater than max_charge_kwh"):
        validate_config(config)

def test_validation_vat_bounds():
    bat = Battery(10, 5, 0, 10, 5, 5)
    config = EnvironmentConfiguration(battery=bat, vat_rate=1.5)
    with pytest.raises(ValueError, match="VAT rate must be between 0 and 1"):
        validate_config(config)