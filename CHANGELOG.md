# Changelog

All notable changes to this project will be documented in this file.

## [0.2.1] - 2025-11-02

### 🐛 Bug Fixes

#### Price Calculation Corrections
- **Fixed DEFAULT_SURCHARGE_PRICE_INCL** from 0.1228 to 0.0123 EUR/kWh (correct Tibber surcharge of ~1.23 cent)
- **Improved electricity_price_calc function** with better debugging information and proper component breakdown
- **Fixed calculated total price sensor** that was showing 0.3264 instead of expected ~0.2284 EUR/kWh due to 10x too high surcharge

#### Development & Documentation
- **Added comprehensive AI development instructions** in `.github/copilot-instructions.md` for coding agents
- **Clarified sensor usage patterns** for consumption vs solar feed-in decisions
- **Updated documentation** to prevent confusion between different price sensors

### ⚠️ Important Notes
- **Existing users**: Please update your configuration via Settings > Devices & Services > Tibber Advanced > Configure
- **Change "Surcharge Price (incl BTW)" from 0.1228 to 0.0123** to get correct price calculations
- **New installations** will automatically use the correct default values

## [0.2.0] - 2025-10-29

### 🎉 Major Improvements

#### Dutch Solar Panel Support
- **Complete README translation to Dutch** - Technical documentation now fully accessible for Dutch users
- **Solar panel automation examples** added to `/examples` directory with detailed Dutch comments
- **Net feed-in tariff template** for calculating real earnings from solar panels considering Dutch "saldering" rules

#### Display Precision
- **Sensor display precision configured** for all 33 sensors:
  - Power sensors: 0 decimals (whole Watts)
  - Energy sensors: 4 decimals (precise kWh)
  - Price sensors: 4 decimals (precise EUR/kWh)
  - Voltage sensors: 1 decimal
  - Current sensors: 2 decimals

#### Error Handling & Logging
- **Improved error messages** - Changed ERROR to WARNING for temporary connection issues
- **Dutch error messages** for better user experience
- **Smart retry logic** - Only show stacktrace after 3+ failed attempts
- **HTTP 504 timeout handling** - Treated as temporary issue, not fatal error

#### Configuration & Options
- **Dynamic configuration support** - Options can now be changed without restart
- **Improved config flow** with proper default values:
  - Surcharge incl BTW: €0.1228 (Tibber default)
  - Tax rate: 21% (Dutch VAT)
  - Energy tax: €0.10154/kWh
- **Automatic surcharge calculation** - excl VAT calculated from incl VAT value

#### Price Data & Sensors
- **Quarter-hourly price resolution** - Changed from hourly to 15-minute intervals
- **Price rank sensors** (0-1 normalized values):
  - `hour_cheapest_top` - Full day comparison
  - `hour_cheapest_top_after_0000` - Night hours (00:00-08:00)
  - `hour_cheapest_top_after_0800` - Day hours (08:00-18:00)
  - `hour_cheapest_top_after_1800` - Evening hours (18:00-00:00)
- **New price sensors**:
  - `electricity_price_surcharge_excl` - Tibber surcharge excl VAT
  - `electricity_price_surcharge_incl` - Tibber surcharge incl VAT
  - `electricity_energy_tax_excl` - Energy tax excl VAT (configured)
  - `electricity_energy_tax_incl` - Energy tax incl VAT
- **Improved sensor names and descriptions** in translations
- **Compact price_info_summary** attribute to avoid database bloat
- **Currency fallback** to EUR when not available from API

### 📝 Documentation

#### New Example Files
- `automation_batterij_laden.yaml` - Automatic battery charging at negative prices
- `automation_teruglevering_schakelen.yaml` - Smart solar feed-in control
- `dashboard_prijzen_grafiek.yaml` - ApexCharts price visualization
- `dashboard_zonnepanelen_status.yaml` - Solar panel status dashboard
- `template_teruglevering_netto_tarief.yaml` - Net feed-in rate calculation
- `solar_feedin_control.yaml` - Marked as deprecated, redirects to new examples

#### Enhanced README
- Complete Dutch solar panel guide (135+ lines)
- Quarter-hourly data explanation
- Sensor usage examples
- Automation templates
- Dashboard card examples

### 🔧 Technical Changes

#### Core Integration
- **Non-blocking SSL context creation** - Off event loop to prevent blocking
- **Improved imports** - Proper exception handling with explicit imports
- **Updated pyTibber requirement** to >=0.32.2
- **Added gql.transport.websockets logger** to loggers list in manifest

#### Sensor Platform
- **RT sensor currency detection** - Prefer live measurement, fallback to home info, default to EUR
- **Improved availability checks** for all sensors
- **Entity categories** configured for diagnostic sensors
- **Entity registry** - Diagnostic sensors disabled by default to reduce clutter

#### Coordinator
- **Improved update logic** with proper exception handling
- **Better error recovery** for temporary API issues

#### Translations
- **Enhanced Dutch (nl.json)** - Complete sensor descriptions with state templates
- **Improved English (en.json)** - Detailed sensor explanations
- **Updated German (de.json)** - Complete sensor translations

### 🐛 Bug Fixes
- Fixed price rank calculation to return 0-1 normalized values instead of 1-24
- Fixed template sensor YAML conflict (version 2 properly commented)
- Fixed ApexCharts xaxis configuration for v2.2.3 compatibility
- Fixed broken README link to non-existent automation file
- Fixed ConnectionClosedError logging level (WARNING instead of ERROR)
- Fixed watchdog reconnect logic to use async properly

### 🔒 Security & Performance
- SSL context creation moved off event loop
- Proper async/await usage throughout codebase
- Improved error boundaries to prevent crashes
- Better resource cleanup on disconnection

### 📊 Dashboard & UI
- ApexCharts v2.2.3 compatible configuration
- Solar Bar Card integration examples
- Template sensor for grid power calculation
- Compact status cards with color indicators

### 🌍 Localization
- Full Dutch translation of technical documentation
- Dutch error messages for common issues
- Consistent terminology across all languages

### ⚙️ Configuration
- Config flow improved with proper typing
- Options flow with dynamic updates
- Better default values for Dutch market
- Proper validation and range checking

---

## [0.1] - Previous Release
- Initial release
- Basic Tibber API integration
- Real-time data support
- Price sensors
- Historical data

---

## Migration Guide

### From 0.1 to 0.2.0

#### Breaking Changes
- Price rank sensors now return 0-1 values instead of 1-24
  - Update automations using `< 5` to `< 0.2` (top 20%)
  - Update automations using `> 20` to `> 0.8` (top 20% expensive)

#### Recommended Actions
1. **Review sensor precision** - Some sensors now show fewer decimals
2. **Update automations** if using price rank sensors
3. **Check config options** - New surcharge and tax settings available
4. **Add solar examples** if you have solar panels
5. **Update price calculations** to use quarter-hourly data

#### New Features to Explore
- Solar feed-in automation (if applicable)
- Price visualization dashboard
- Battery charging optimization
- Quarter-hourly price analysis

---

## Notes
- Version 0.2.0 requires Home Assistant 2024.10 or later
- pyTibber >=0.32.2 required for quarter-hourly price support
- Some sensors are now disabled by default - enable in entity registry if needed
