# 🚀 Git Commands voor Release v0.2.0

## Stap 1: Add alle wijzigingen

```powershell
cd c:\PIP\HomeAssistantTibber

# Add alle bestanden
git add .

# Controleer wat er gecommit gaat worden
git status
```

## Stap 2: Commit met uitgebreide message

```powershell
git commit -m "Release v0.2.0 - Quarter-hourly prices & Dutch solar support

Major improvements:
- Quarter-hourly price resolution (15-min intervals)
- Complete Dutch solar panel automation guide with 6 examples
- Display precision configured for all 33 sensors
- Improved error handling with Dutch messages
- Dynamic configuration support (no restart needed)
- Price rank sensors (0-1 normalized scale)
- Currency fallback to EUR for stability
- Compact price_info_summary to avoid DB bloat

New features:
- Solar feed-in automation examples
- Battery charging during negative prices
- ApexCharts & Solar Bar Card dashboards
- Net feed-in tariff template sensor
- HACS integration support

Technical improvements:
- Non-blocking SSL context creation
- Proper async/await throughout codebase
- Improved exception handling
- Better resource cleanup
- Quarter-hourly GraphQL queries

Documentation:
- Complete README with installation instructions
- CHANGELOG.md with detailed release notes
- CONTRIBUTING.md for contributors
- GitHub Actions CI/CD pipeline
- Issue templates for bug reports & features

Installation clarification:
- Repository name: HomeAssistantTibber
- Integration domain: tibber_adv
- Install location: /custom_components/tibber_adv/
- HACS handles this automatically

Breaking changes:
- Price rank sensors now return 0-1 instead of 1-24
- Update automations: <5 becomes <0.2, >20 becomes >0.8

Full details in CHANGELOG.md"
```

## Stap 3: Tag de release

```powershell
# Maak een annotated tag
git tag -a v0.2.0 -m "Version 0.2.0 - Quarter-hourly prices & Dutch solar support

Major release with quarter-hourly price data, complete Dutch solar panel 
automation support, and extensive documentation improvements.

Highlights:
- 15-minute price intervals
- 6 new YAML automation examples
- Improved error handling
- Dynamic configuration
- HACS integration ready
- Multi-language support (NL, EN, DE)

See CHANGELOG.md for complete details."

# Controleer de tag
git tag -l -n9 v0.2.0
```

## Stap 4: Push naar GitHub

```powershell
# Push de main branch
git push origin main

# Push de tag
git push origin v0.2.0
```

## Stap 5: Controleer op GitHub

Na de push:
1. Ga naar: https://github.com/OdynBrouwer/HomeAssistantTibber
2. Controleer dat alle bestanden zichtbaar zijn
3. Kijk of de GitHub Actions workflow draait (groene vinkje)

## Stap 6: Maak GitHub Release

1. Ga naar: https://github.com/OdynBrouwer/HomeAssistantTibber/releases/new
2. Selecteer tag: `v0.2.0`
3. Release title: **Version 0.2.0 - Quarter-Hourly Prices & Dutch Solar Support**
4. Beschrijving (kopieer onderstaande):

```markdown
## 🎉 Major Release - Quarter-Hourly Price Data & Dutch Solar Support

### ✨ Highlights

- 📊 **Quarter-hourly price resolution** - 15-minute intervals instead of hourly
- 🌞 **Complete Dutch solar panel guide** - 6 automation/dashboard examples
- 💰 **Smart feed-in control** - Avoid negative prices, maximize earnings
- 🔋 **Battery automation** - Charge during negative prices
- ⚡ **Dynamic configuration** - Change settings without restart
- 🎯 **Display precision** - Configured for all 33 sensors
- 🇳🇱 **Dutch translations** - Error messages and documentation

### 📦 Installation

**Via HACS (Recommended):**
1. Add custom repository: `https://github.com/OdynBrouwer/HomeAssistantTibber`
2. Install "Tibber Advanced"
3. Restart Home Assistant
4. Add integration with your Tibber API token

**Important**: Repository is named `HomeAssistantTibber`, but installs as `tibber_adv` - HACS handles this automatically!

### 🆕 New Features

**Solar Panel Optimization:**
- Automatic feed-in control based on real-time prices
- Net feed-in tariff calculation (Dutch "saldering")
- Battery charging during negative prices
- Dashboard examples with ApexCharts & Solar Bar Card

**Price Sensors:**
- Price rank sensors (0-1 normalized scale)
- Quarter-hourly price data from Tibber API
- Detailed price breakdown (spot, surcharges, taxes)
- Currency fallback to EUR for stability

**Configuration:**
- Dynamic tax rate configuration
- Custom surcharge settings
- Energy tax per kWh
- All configurable without restart

### 📝 Documentation

- Complete Dutch solar automation guide
- 6 new YAML examples in `/examples`
- Installation instructions for HACS & manual
- CONTRIBUTING.md for developers
- Detailed CHANGELOG.md

### ⚠️ Breaking Changes

**Price rank sensors** now return 0-1 values (was 1-24):
- Update automations: `< 5` becomes `< 0.2` (cheapest 20%)
- Update automations: `> 20` becomes `> 0.8` (most expensive 20%)

### 📊 Statistics

- 16 files modified
- 9 new files added
- 33 sensors with display precision
- 6 automation/dashboard examples
- 3 languages (NL, EN, DE)

### 🔗 Links

- **Documentation**: [README.md](https://github.com/OdynBrouwer/HomeAssistantTibber/blob/main/README.md)
- **Changelog**: [CHANGELOG.md](https://github.com/OdynBrouwer/HomeAssistantTibber/blob/main/CHANGELOG.md)
- **Examples**: [examples/](https://github.com/OdynBrouwer/HomeAssistantTibber/tree/main/examples)
- **Contributing**: [CONTRIBUTING.md](https://github.com/OdynBrouwer/HomeAssistantTibber/blob/main/CONTRIBUTING.md)

### 🙏 Credits

Thanks to:
- @danielhiversen for the original Tibber integration
- Tibber for the excellent API
- All contributors and testers

---

**Full changelog**: https://github.com/OdynBrouwer/HomeAssistantTibber/blob/main/CHANGELOG.md
```

5. Klik op **Publish release**

## ✅ Post-Release Checklist

- [ ] Controleer GitHub Actions (moet groen zijn)
- [ ] Test HACS installatie
- [ ] Verifieer dat alle links werken
- [ ] Monitor issues voor feedback
- [ ] Deel op Home Assistant community (optioneel)

## 🎯 Klaar!

Je release is nu live! 🚀

Gebruikers kunnen installeren via:
- HACS custom repository
- Handmatige download van releases page
- Git clone voor developers

**Belangrijk**: De repository heet `HomeAssistantTibber` maar installeert als `tibber_adv` - dit staat nu duidelijk in alle documentatie!
