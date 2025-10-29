"""Constants for Tibber integration."""

DATA_HASS_CONFIG = "tibber_adv_hass_config"
DOMAIN = "tibber_adv"
MANUFACTURER = "Tibber"

# Configuration constants
CONF_SURCHARGE_PRICE_INCL = "surcharge_price_incl"
CONF_TAX_RATE = "tax_rate"
CONF_TAX_PER_KWH = "tax_per_kwh"

# Default values
DEFAULT_SURCHARGE_PRICE_INCL = 0.1228  # Tibber surcharge incl BTW
DEFAULT_TAX_RATE = 21.0  # BTW percentage
DEFAULT_TAX_PER_KWH = 0.10154  # Energiebelasting per kWh
