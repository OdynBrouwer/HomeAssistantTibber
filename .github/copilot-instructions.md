# Tibber Advanced Integration - AI Assistant Instructions

## Project Overview
This is a Home Assistant custom integration (`tibber_adv`) providing advanced Tibber electricity price monitoring with quarter-hourly resolution and Dutch market specialization. Fork of the official Tibber integration with enhanced solar panel optimization features.

## Key Architecture Components

### Core Structure
- **Domain**: `tibber_adv` (not `tibber` - this is critical for avoiding conflicts)
- **Main entry**: `__init__.py` handles setup and creates Tibber connection with custom tax/surcharge parameters
- **Data flow**: `coordinator.py` → `sensor.py` → Home Assistant entities
- **API wrapper**: Custom `tibber/` module with GraphQL queries and price calculations

### Price Sensor Hierarchy
The integration creates multiple price sensors with specific Dutch market logic:

```python
# For CONSUMPTION decisions (total cost):
sensor.electricity_price_total_incl_vat  # Official Tibber API price - USE THIS!

# For SOLAR FEED-IN decisions (spot price only):
sensor.electricity_base_price_without_surcharge  # Can go negative!

# Price breakdown sensors:
sensor.electricity_price_energy_tax_incl_vat    # Energy tax component
sensor.electricity_price_surcharge_incl         # Tibber surcharge

# Debug sensor (disabled by default):
sensor.electricity_price_total_incl_vat_calculated  # Manual calculation for debugging
```

**Critical**: 
- For consumption: Always use `electricity_price_total_incl_vat` (official Tibber API price)
- For solar feed-in: Always use `electricity_base_price_without_surcharge` (spot price only)
- Never use the `_calculated` sensor for real automation - it's for debugging only

## Dutch Solar Panel Specialization

### Net Metering Rules ("Saldering")
Two calculation periods with different logic:
- **Until 2027**: Feed-in = `(spot_price × 1.21) + energy_tax_refund`
- **After 2027**: Feed-in = `spot_price × 1.21` (no energy tax refund)

### Template Patterns
Reference `examples/template_teruglevering_netto_tarief.yaml` for:
- Net feed-in rate calculations respecting Dutch regulations
- Conditional logic for before/after 2027 rules
- Proper sensor naming with `tibber_pulse_JOUW_ADRES_` prefix

### Automation Patterns
Reference `examples/automation_teruglevering_schakelen.yaml` for:
- Inverter switching based on negative price detection
- State change triggers with proper from/to conditions
- Notification patterns with meaningful Dutch messages

## Configuration Flow
- `config_flow.py`: Token validation via GraphQL, options for tax rates and surcharges
- Required: `CONF_ACCESS_TOKEN` from developer.tibber.com
- Optional: `CONF_BTW_PERCENTAGE`, `CONF_PURCHASING_COMPENSATION`, `CONF_ELECTRICITY_ENERGY_TAX_INCL_BTW`

## Development Patterns

### Sensor Creation
Always use `TibberSensorEntityDescription` with:
- `key`: Internal identifier
- `translation_key`: References `strings.json` and `translations/`
- Native unit handling for EUR/kWh vs cent/kWh variants

### Error Handling
Custom exceptions in `tibber/exceptions.py`:
- `RetryableHttpExceptionError`: Temporary API issues
- `FatalHttpExceptionError`: Permanent failures requiring user intervention

### Testing & Validation
- HACS validation required for all changes
- Hassfest validation for Home Assistant compliance
- No pytest setup - relies on HA validation tools

## Critical Constants
```python
# Domain and identification
DOMAIN = "tibber_adv"                    # Never change this
MANUFACTURER = "Tibber"

# Dutch market defaults (2024/2025)
DEFAULT_BTW_PERCENTAGE = 21.0                  # BTW percentage
DEFAULT_ELECTRICITY_ENERGY_TAX_INCL_BTW = 0.1228   # Energiebelasting incl BTW per kWh (2024/2025)
DEFAULT_PURCHASING_COMPENSATION = 0.0205        # Tibber inkoopvergoeding excl BTW
```

## File Naming Convention
When working with examples or documentation:
- Repository name: `HomeAssistantTibber`
- Integration folder: `tibber_adv`
- User sensor names: `tibber_pulse_[ADDRESS]_[sensor_type]`

## Common Pitfalls
1. **Domain confusion**: Always use `tibber_adv`, not `tibber`
2. **Price sensor misuse**: Don't use total price for solar decisions
3. **Dutch regulations**: Solar calculations change significantly in 2027
4. **Sensor naming**: User examples need actual address replacement
5. **Translation keys**: Must match between `strings.json` and translation files