# Installation Note

## Repository Name vs Integration Domain

**Important**: This repository is named `HomeAssistantTibber` on GitHub, but the integration domain is `tibber_adv`.

### Why?
- **GitHub Repository**: `HomeAssistantTibber` (descriptive name for discovery)
- **Integration Domain**: `tibber_adv` (defined in manifest.json)
- **Install Location**: `/config/custom_components/tibber_adv/`

### HACS Installation
HACS automatically handles this correctly. When you install via HACS, it will:
1. Download from `HomeAssistantTibber` repository
2. Install to `/config/custom_components/tibber_adv/` folder
3. Register the integration as `tibber_adv`

### Manual Installation
If installing manually:
1. Download or clone this repository
2. Copy/rename the folder to `tibber_adv`
3. Place in `/config/custom_components/tibber_adv/`
4. Restart Home Assistant

**Do NOT** copy the folder as `HomeAssistantTibber` - it must be `tibber_adv`!

### Folder Structure
```
/config/
└── custom_components/
    └── tibber_adv/          ← Correct name!
        ├── __init__.py
        ├── manifest.json    (domain: "tibber_adv")
        ├── config_flow.py
        ├── sensor.py
        ├── tibber/
        └── ...
```

### After Installation
The integration will appear as "Tibber Advanced" in:
- Settings > Devices & Services
- HACS > Integrations

But internally it uses the domain `tibber_adv` for all entity IDs and services.
