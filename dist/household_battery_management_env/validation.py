from .domain import EnvironmentConfiguration
import logging

logger = logging.getLogger(__name__)

def validate_config(config: EnvironmentConfiguration) -> EnvironmentConfiguration:
    """
    Validates and coerces EnvironmentConfiguration settings.
    
    Args:
        config: The configuration to validate.
        
    Returns:
        A validated (and potentially coerced) EnvironmentConfiguration.
        
    Raises:
        ValueError: If a setting is invalid and cannot be safely coerced.
    """
    # 1. Battery Limits Validation
    if config.battery.capacity_kwh <= 0:
        raise ValueError(f"Battery capacity must be positive. Got: {config.battery.capacity_kwh}")
    
    if config.battery.min_charge_kwh < 0:
        logger.warning("Coercing negative min_charge_kwh to 0.0")
        config.battery.min_charge_kwh = 0.0
        
    if config.battery.max_charge_kwh > config.battery.capacity_kwh:
        logger.warning("Coercing max_charge_kwh to match battery capacity")
        config.battery.max_charge_kwh = config.battery.capacity_kwh

    if config.battery.min_charge_kwh > config.battery.max_charge_kwh:
        raise ValueError(
            f"min_charge_kwh ({config.battery.min_charge_kwh}) cannot be greater "
            f"than max_charge_kwh ({config.battery.max_charge_kwh})"
        )

    # 2. Current Charge Clipping
    if config.battery.current_charge_kwh < config.battery.min_charge_kwh:
        logger.warning("Clipping initial charge to min_charge_kwh")
        config.battery.current_charge_kwh = config.battery.min_charge_kwh
    elif config.battery.current_charge_kwh > config.battery.max_charge_kwh:
        logger.warning("Clipping initial charge to max_charge_kwh")
        config.battery.current_charge_kwh = config.battery.max_charge_kwh

    # 3. Rate Limits
    if config.battery.charge_rate_kw < 0:
        raise ValueError(f"charge_rate_kw must be non-negative. Got: {config.battery.charge_rate_kw}")
    if config.battery.discharge_rate_kw < 0:
        raise ValueError(f"discharge_rate_kw must be non-negative. Got: {config.battery.discharge_rate_kw}")

    # 4. Simulation Duration
    if config.days <= 0:
        raise ValueError(f"Simulation days must be at least 1. Got: {config.days}")

    # 5. Slovenian Tariff System (MVP requires 5 levels)
    lists_to_check = {
        "tariff_energy_rates": config.tariff_energy_rates,
        "tariff_power_rates": config.tariff_power_rates,
        "agreed_power_kw": config.agreed_power_kw
    }
    for name, lst in lists_to_check.items():
        if len(lst) != 5:
            raise ValueError(f"SlovenianTariffSystem requires exactly 5 entries for {name}. Found {len(lst)}.")
        if any(v < 0 for v in lst):
            raise ValueError(f"All values in {name} must be non-negative.")

    # 6. VAT and Fees
    if not (0 <= config.vat_rate <= 1.0):
         raise ValueError(f"VAT rate must be between 0 and 1 (decimal fraction). Got: {config.vat_rate}")
    
    if config.fixed_fee_monthly < 0:
        logger.warning("Coercing negative fixed_fee_monthly to 0.0")
        config.fixed_fee_monthly = 0.0

    return config