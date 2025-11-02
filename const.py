"""Constants for Tibber integration."""

DATA_HASS_CONFIG = "tibber_adv_hass_config"
DOMAIN = "tibber_adv"
MANUFACTURER = "Tibber"

# Configuration constants
CONF_ELECTRICITY_ENERGY_TAX_INCL_BTW = "electricity_energy_tax_incl_btw"
CONF_BTW_PERCENTAGE = "btw_percentage"
CONF_PURCHASING_COMPENSATION = "purchasing_compensation"

# Default values
DEFAULT_ELECTRICITY_ENERGY_TAX_INCL_BTW = 0.1228  # Energiebelasting incl BTW per kWh (2024/2025)
DEFAULT_BTW_PERCENTAGE = 21.0  # BTW percentage
DEFAULT_PURCHASING_COMPENSATION = 0.0205  # Inkoopvergoeding excl BTW per kWh
