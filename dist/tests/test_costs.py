import pytest
from household_battery_management_env.domain import (
    Battery, EnvironmentConfiguration, ElectricityPrice, TariffBlock
)
from household_battery_management_env.tariff_logic import calculate_step_cost

@pytest.fixture
def base_config():
    bat = Battery(10, 5, 2, 10, 5, 5)
    return EnvironmentConfiguration(battery=bat, vat_rate=0.0) # 0 VAT for easier manual check

def test_fixed_fee_only(base_config):
    # Zero grid use, cost should only be the fixed fee
    prices = ElectricityPrice(0.15, 0.05)
    block = TariffBlock(3, False)
    cost = calculate_step_cost(0.0, block, prices, base_config)
    
    # 5.0 EUR / (30 days * 24h * 4 steps) = 0.001736...
    assert cost == pytest.approx(5.0 / (30 * 24 * 4))

def test_import_cost(base_config):
    prices = ElectricityPrice(0.10, 0.05)
    block = TariffBlock(1, True) # Tariff energy rate 0.02
    # Import 10 kWh in 15 mins (40 kW)
    # Agreed power is 5kW
    # Cost = 10 * (0.10 + 0.02) + Excess penalty + fixed fee
    cost = calculate_step_cost(10.0, block, prices, base_config)
    assert cost > 1.20 # 10 * 0.12

def test_export_reduction(base_config):
    prices = ElectricityPrice(0.15, 0.10)
    block = TariffBlock(3, False)
    # Export 2 kWh
    cost_export = calculate_step_cost(-2.0, block, prices, base_config)
    cost_zero = calculate_step_cost(0.0, block, prices, base_config)
    
    # Export should be cheaper (more negative) than zero use
    assert cost_export < cost_zero
    assert cost_export == pytest.approx(-0.2 + (5.0 / (30 * 24 * 4)))

def test_vat_application(base_config):
    config_with_vat = EnvironmentConfiguration(battery=base_config.battery, vat_rate=0.22)
    prices = ElectricityPrice(0.10, 0.05)
    block = TariffBlock(1, True)
    cost_no_vat = calculate_step_cost(1.0, block, prices, base_config)
    cost_vat = calculate_step_cost(1.0, block, prices, config_with_vat)
    
    assert cost_vat == pytest.approx(cost_no_vat * 1.22)