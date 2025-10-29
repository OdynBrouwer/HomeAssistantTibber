# Tibber Advanced Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![GitHub Release](https://img.shields.io/github/release/mupsje/HomeAssistantTibber.svg)](https://github.com/OdynBrouwer/HomeAssistantTibber/releases)
[![License](https://img.shields.io/github/license/mupsje/HomeAssistantTibber.svg)](LICENSE)
[![Validate](https://github.com/OdynBrouwer/HomeAssistantTibber/workflows/Validate/badge.svg)](https://github.com/OdynBrouwer/HomeAssistantTibber/actions)

Advanced fork of the Home Assistant Tibber component with **quarter-hourly price data**, **solar panel optimization**, and **Dutch market support**.

## ✨ Features

- 📊 **Quarter-hourly price resolution** - 15-minute price intervals instead of hourly
- 🌞 **Solar panel optimization** - Smart feed-in control based on real-time prices
- 💰 **Detailed price breakdown** - Base price, surcharges, and taxes shown separately
- 🇳🇱 **Dutch net metering support** - Proper "saldering" calculations for solar panels
- ⚡ **Dynamic configuration** - Change settings without restart
- 🔋 **Battery automation examples** - Charge during negative prices
- 📈 **Price ranking sensors** - Compare prices across different time periods (0-1 scale)
- 🎯 **High precision display** - Configurable decimal places per sensor type
- 🌐 **Multi-language** - Dutch, English, German translations

## 📦 Installation

### Method 1: HACS (Recommended)

1. Add this repository as a custom repository in HACS:
   - Go to HACS > Integrations
   - Click the 3 dots menu (top right) > Custom repositories
   - Add URL: `https://github.com/OdynBrouwer/HomeAssistantTibber`
   - Category: Integration
   - Click Add

2. Install via HACS:
   - Search for "Tibber Advanced" in HACS
   - Click Install
   - Restart Home Assistant

3. Add the integration:
   - Go to Settings > Devices & Services
   - Click "+ Add Integration"
   - Search for "Tibber Advanced"
   - Enter your Tibber API token

### Method 2: Manual Installation

1. Download this repository
2. Copy the **entire folder** to your Home Assistant:
   ```
   # The folder structure should be:
   /config/custom_components/tibber_adv/
   ├── __init__.py
   ├── manifest.json
   ├── config_flow.py
   ├── sensor.py
   ├── tibber/
   │   ├── __init__.py
   │   └── ...
   └── ...
   ```
   
   **Important**: The folder must be named `tibber_adv` (not `HomeAssistantTibber`)!

3. Restart Home Assistant
4. Add the integration via Settings > Devices & Services

### Getting Your Tibber API Token

1. Go to [Tibber Developer Portal](https://developer.tibber.com/settings/access-token)
2. Login with your Tibber account
3. Create a new token (give it a name like "Home Assistant")
4. Copy the token (you'll need it during setup)

**Note**: The repository name is `HomeAssistantTibber`, but it must be installed as `tibber_adv` in your custom_components folder. HACS does this automatically!

## 🌞 Zonnepanelen Automatisering (Voor Nederlanders)

### Welke sensor moet ik gebruiken?

**Let op! Dit is belangrijk om te begrijpen:**

#### ✅ Voor **VERBRUIK** beslissingen:
Gebruik: **`sensor.electricity_price_total_incl_vat`** (of `electricity_price`)

Dit is de **totale prijs** die je betaalt als je stroom **gebruikt**:
- Nord Pool spotprijs
- Tibber fee (service kosten)
- Energiebelasting
- BTW op alles

**Let op:** Netbeheerkosten zitten hier NIET in - die worden apart per maand gefactureerd door je netbeheerder.

**Voorbeeld:** Als deze sensor €0.30/kWh toont, betaal je 30 cent voor elke kWh die je gebruikt (plus maandelijkse netbeheerkosten op je factuur).

#### ✅ Voor **TERUGLEVERING** beslissingen (zonnepanelen):
Gebruik: **`sensor.electricity_base_price_without_surcharge`** (of `electricity_price_excl_base`)

Dit is de **spotprijs** van Nord Pool, **zonder** extra kosten:
- **Kan negatief worden!** (Bij veel zon en weinig vraag)
- Dit is wat je terugkrijgt via saldering (+ energiebelasting tot 2027)
- **NIET** de totale prijs gebruiken voor teruglevering!

**Voorbeeld:** Als deze sensor -€0.05/kWh toont, betaal je 5 cent per kWh als je terugleverd (negatieve prijs!)

---

### 📅 Saldering Regels in Nederland

#### Tot 2027 (NU):
Bij teruglevering krijg je terug:
1. **Spotprijs × 1.21** (BTW op spotprijs)
2. **+ Energiebelasting terugbetaald** (€0.12286 per kWh in 2025)

**Formule:**
```
teruglevering_netto = (spotprijs × 1.21) + 0.12286
```

**Voorbeeld bij spotprijs -€0.05/kWh:**
```
(-0.05 × 1.21) + 0.12286 = -0.0605 + 0.12286 = +€0.06236/kWh
```
✅ **Je krijgt nog steeds geld!** Dankzij energiebelasting terugbetaling.

#### Na 2027 (TOEKOMST):
Je krijgt **ALLEEN** de spotprijs terug (geen energiebelasting meer):
```
teruglevering_netto = spotprijs × 1.21
```

**Voorbeeld bij spotprijs -€0.05/kWh:**
```
-0.05 × 1.21 = -€0.0605/kWh
```
❌ **Je betaalt geld om terug te leveren!** Bij negatieve prijzen.

---

### 🤖 Complete Automatisering voor Zonnepanelen

**Volledige voorbeelden beschikbaar in de `/examples` map:**

- **Template sensor:** [`examples/template_teruglevering_netto_tarief.yaml`](examples/template_teruglevering_netto_tarief.yaml)
  - Versie voor tot 2027 (met energiebelasting terugbetaling)
  - Versie voor na 2027 (alleen spotprijs)

- **Automatisering omvormer aan/uit:** [`examples/automation_teruglevering_schakelen.yaml`](examples/automation_teruglevering_schakelen.yaml)
  - Schakelt automatisch bij positief/negatief
  - Inclusief notificaties
  - Met uitleg welke switch je moet aanpassen

- **Dashboard kaart:** [`examples/dashboard_zonnepanelen_status.yaml`](examples/dashboard_zonnepanelen_status.yaml)
  - Overzicht van alle relevante sensoren
  - Status teruglevering
  - Huidige productie

---

### 🎯 Hoe werkt dit?

1. **Template sensor berekent netto tarief:**
   - Pakt spotprijs van Tibber API
   - Rekent BTW (× 1.21)
   - Telt energiebelasting erbij (tot 2027)
   - Resultaat: wat je écht overhoudt per kWh

2. **Automatisering kijkt naar overgangen:**
   - **Van positief naar negatief** → Omvormer UIT
   - **Van negatief naar positief** → Omvormer AAN
   - Stuurt notificatie zodat je weet wat er gebeurt

3. **Je bespaart geld door:**
   - Niet terug te leveren bij negatieve prijzen
   - Stroom lokaal te gebruiken (batterij, boiler, etc.)
   - Automatisch te schakelen zonder er naar om te kijken

---

### 💡 Extra Tips

**Alternatieve strategieën:**
- **Batterij laden bij negatieve prijzen** - zie [`examples/automation_batterij_laden.yaml`](examples/automation_batterij_laden.yaml)
- **cd c:\PIP\HomeAssistantTibber

# 1. Add alle wijzigingen
git add .

# 2. Commit
git commit -m "Release v0.2.0 - Quarter-hourly prices & Dutch solar support"

# 3. Tag
git tag -a v0.2.0 -m "Version 0.2.0"

# 4. Push
git push origin main
git push origin v0.2.0Historische data visualisatie** - zie [`examples/dashboard_prijzen_grafiek.yaml`](examples/dashboard_prijzen_grafiek.yaml)

**Veelvoorkomende omvormer switches:**
- Growatt: `switch.growatt_export_control`
- SolarEdge: `switch.solaredge_export_limit`
- Huawei: `switch.huawei_grid_export`
- Enphase: `switch.enphase_grid_profile`
- Omnik/Solis: `switch.solis_export_power_management`

---

## Prijsberekening Sensoren

### Basis Prijs Componenten
- `electricity_price`: Huidige totaalprijs per kWh van Tibber API
- `electricity_price_excl_base`: Ruwe basisprijs zonder toeslagen

### Toeslag Componenten
- `electricity_price_surcharge_excl`: Extra kosten per kWh voor BTW
- `electricity_price_surcharge_incl`: Toeslag inclusief BTW
- `electricity_price_excl`: Basisprijs + toeslag (geen belasting)

### Belasting Componenten
- `electricity_price_energy_tax_excl`: Energiebelasting voor BTW
- `electricity_price_energy_tax_incl`: Energiebelasting inclusief BTW
- `tax_rate`: Huidig BTW percentage

### Totaal Prijs
- `electricity_price_calc`: Totaalprijs berekend als:
  ```
  basisprijs + toeslag + energiebelasting * (1 + btw_tarief/100)
  ```

## Verbruik en Kosten Sensoren

### Energie Metingen
- `accumulated_consumption`: Totaal verbruik sinds installatie in kWh
- `accumulated_production`: Totale productie sinds installatie in kWh
- `accumulated_consumption_last_hour`: kWh verbruikt in huidige uur
- `accumulated_production_last_hour`: kWh geproduceerd in huidige uur
- `month_cons`: Totaal verbruik deze maand

### Financiële Tracking
- `accumulated_cost`: Totale kosten op basis van historische prijzen per uur
- `accumulated_reward`: Tegoed verdiend met teruglevering
- `month_cost`: Totale kosten deze maand

### Vermogen Monitoring
- `power`: Huidig vermogensverbruik in watts
- `average_power`: Gemiddeld vermogen over het laatste uur
- `min_power`: Minimum vermogen in laatste uur
- `max_power`: Maximum vermogen in laatste uur
- `power_production`: Huidige productie in watts
- `power_factor`: Vermogensfactor kwaliteitsindicator (ideaal: 1.0)

### Driefasen Metingen
- `voltage_phase1`: Spanning op L1 (230V nominaal)
- `voltage_phase2`: Spanning op L2 (230V nominaal)
- `voltage_phase3`: Spanning op L3 (230V nominaal)
- `current_l1`: Stroomsterkte op L1
- `current_l2`: Stroomsterkte op L2
- `current_l3`: Stroomsterkte op L3

## Tijd-gebaseerde Functies

### Prijs Rangschikking Sensoren
Geeft aan of het huidige uur binnen de X goedkoopste uren valt. Geeft positie terug (bijv. "3" betekent 3e goedkoopste) of null als niet in top X:

- `hour_cheapest_top`: Rangschikking over alle uren vandaag
- `hour_cheapest_top_after_0000`: Nacht rangschikking (00:00-08:00)
- `hour_cheapest_top_after_0800`: Dag rangschikking (08:00-18:00)
- `hour_cheapest_top_after_1800`: Avond rangschikking (18:00-00:00)

Gebruiksvoorbeeld: Stel X=4 in om de 4 goedkoopste uren te identificeren voor het draaien van je warmtepomp.

### Tijdstempel Sensoren
- `peak_hour_time`: Tijdstempel van hoogste verbruiksuur
- `last_price_update`: Laatste keer dat prijsgegevens zijn ontvangen

### Piek Verbruik Tracking
- `peak_hour`: Hoogste verbruik in kWh voor enig uur
- `estimatedHourConsumption`: Verwacht verbruik voor huidige uur

### Diagnostiek
- `signal_strength`: Meterkoppeling kwaliteit in dB
- `last_meter_consumption`: Laatste gerapporteerde meterstand verbruik
- `last_meter_production`: Laatste gerapporteerde meterstand productie

## Prijsberekening Voorbeeld

Voor een basisprijs van €0.20/kWh, toeslag van €0.05/kWh, energiebelasting van €0.12/kWh, en 21% BTW:

1. Basis componenten:
   - `electricity_price_excl_base` = €0.20
   - `electricity_price_surcharge_excl` = €0.05
   - `electricity_price_energy_tax_excl` = €0.12

2. Totaal voor BTW:
   - `electricity_price_excl` = €0.20 + €0.05 = €0.25

3. Belasting berekeningen:
   - BTW op toeslag: €0.05 * 0.21 = €0.0105
   - BTW op energiebelasting: €0.12 * 0.21 = €0.0252
   - BTW op basisprijs: €0.20 * 0.21 = €0.042

4. Eindprijs:
   - `electricity_price_calc` = €0.25 + €0.12 + (€0.0105 + €0.0252 + €0.042)
   - Totaal = €0.4477/kWh

## Technische Specificaties

### Vermogen Metingen
- `power`: Realtime vermogensme ting, geüpdatet elke 2-3 seconden
- `average_power`: Voortschrijdend gemiddelde over 1 uur
- Resolutie: 1 watt
- Maximum waarde: 999999 watts
- Negatieve waarden duiden op stroomproductie

### Spanning Monitoring
- Nominale spanning: 230V per fase
- Acceptabel bereik: 207V - 253V (±10%)
- Update frequentie: Elke 2-3 seconden
- Resolutie: 0.1V

### Stroom Metingen
- Bereik: 0-100A per fase
- Resolutie: 0.1A
- Vermogensfactor bereik: 0-1 (1 = perfect, <0.95 duidt op problemen)
- Fase hoek monitoring inbegrepen in vermogensfactor

### Energie Accumulatie
- `accumulated_consumption`: Non-volatile, overleeft stroomuitval
- Resolutie: 0.001 kWh
- Maximum waarde: 999999999.999 kWh
- Aparte dag/nacht tarief ondersteuning via Tibber API
- Historische data bewaring: Tot 1 jaar

### Prijs Update Frequentie
- Realtime prijzen: Elk uur geüpdatet
- Historische prijzen: Dagelijks geüpdatet om middernacht
- Spotmarkt prijzen: 24 uur van tevoren beschikbaar
- Prijs resolutie: 0.0001 valuta-eenheden

## Automatisering Voorbeelden

### 1. Slimm Elektrische Auto Laden
```yaml
automation:
  - alias: "Start EV Charging at Cheapest Hours"
    trigger:
      - platform: state
        entity_id: sensor.hour_cheapest_top
    condition:
      - condition: numeric_state
        entity_id: sensor.hour_cheapest_top
        below: 4  # One of the 3 cheapest hours
      - condition: numeric_state
        entity_id: sensor.ev_battery_level
        below: 80  # Battery below 80%
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ev_charger
```

### 2. Heat Pump Optimization
```yaml
automation:
  - alias: "Boost Water Heating During Low Price"
    trigger:
      - platform: time_pattern
        minutes: "1"
    condition:
      - condition: or
        conditions:
          - condition: numeric_state
            entity_id: sensor.hour_cheapest_top_after_0000
            below: 3  # Top 2 cheapest night hours
          - condition: numeric_state
            entity_id: sensor.hour_cheapest_top_after_0800
            below: 3  # Top 2 cheapest day hours
      - condition: numeric_state
        entity_id: sensor.water_tank_temp
        below: 55  # Current temperature below target
    action:
      - service: climate.set_temperature
        target:
          entity_id: climate.water_heater
        data:
          temperature: 60
```

### 3. Slimme Zonnepanelen Teruglevering Controle

**Zie de complete handleiding hierboven:** [🌞 Zonnepanelen Automatisering](#-zonnepanelen-automatisering-voor-nederlanders)

Voor Nederlandse gebruikers met zonnepanelen, de automatisering doet automatisch:
- Schakelt teruglevering UIT wanneer prijzen negatief worden
- Schakelt teruglevering AAN wanneer prijzen positief worden
- Houdt rekening met Nederlandse salderingsregels tot 2027
- Stuurt notificaties bij schakelen

Volledige implementatie beschikbaar in de handleiding hierboven en in `examples/solar_feedin_control.yaml`.

### 4. Dynamische Prijs Waarschuwing
```yaml
automation:
  - alias: "Hoge Prijs Waarschuwing"
    trigger:
      - platform: numeric_state
        entity_id: sensor.electricity_price_calc
        above: 0.50  # Prijs boven €0.50 per kWh
    action:
      - service: notify.mobile_app
        data:
          title: "⚠️ Hoge Energieprijs Waarschuwing"
          message: "Huidige prijs: {{ states('sensor.electricity_price_calc') }}
                   Overweeg om niet-essentiële apparaten uit te schakelen."
      - service: switch.turn_off
        target:
          entity_id: 
            - switch.pool_heater
            - switch.towel_radiator
            - switch.decorative_lighting
```

![Screenshot 2024-06-01 at 14-07-20 Instellingen – Home Assistant](https://github.com/OdynBrouwer/HomeAssistantTibber/assets/2556592/67eebb76-9e70-447b-bedd-5935c6003587)


Overzicht van beschikbare sensoren (basisprijs getoond hier is €0.00)
![Screenshot 2024-06-01 at 14-11-57 Overzicht – Home Assistant](https://github.com/OdynBrouwer/HomeAssistantTibber/assets/2556592/7450e953-2285-4f48-bbff-2f6fbf74a1b6)


Nuttig voor mensen met overtollige zonne-energie in Nederland, waar je saldering krijgt voor geproduceerde zonne-energie tot 2027.

## Geavanceerde Technische Informatie

### Sensor Update Gedrag

#### Realtime Sensoren
- `power`, `voltage_*`, `current_*`:
  - Update interval: 2-3 seconden
  - Timeout: 30 seconden (markeert als niet beschikbaar)
  - Herverbinding: Automatisch met exponentiële backoff
  - WebSocket keepalive: 30 seconden ping/pong

#### Prijs Sensoren
- `electricity_price_*`:
  - Nord Pool markt update: 13:00 CET
  - Prijs geldigheid: Hele uur periodes
  - Cache duur: 24 uur
  - Precisie: 6 decimalen

#### Accumulatie Sensoren
- `accumulated_*`:
  - Reset gedrag: Behoudt waarde na herstart
  - Overflow afhandeling: Rolt over bij 1000000000
  - Ontbrekende data: Geïnterpoleerd vanaf laatst bekende waarde
  - Historische data: 1-uur resolutie, 1-jaar bewaring

### Bekende Beperkingen

1. Prijs Berekeningen
   - Belasting berekeningen afronden op 6 decimalen
   - BTW wordt per component berekend om afrondingsfouten te voorkomen
   - Alle tussentijdse berekeningen behouden volledige precisie

2. Vermogen Metingen
   - Enkelfase woningen: Alleen L1 waarden zijn zinvol
   - Vermogensfactor nauwkeurigheid: ±2%
   - Maximum meetbare stroom: 100A per fase
   - Minimum meetbaar vermogen: 1W

3. Historische Data
   - Uur grensovergangen kunnen kleine gaten vertonen
   - Zomertijd wijzigingen kunnen dubbele of ontbrekende uren tonen
   - Historische prijzen beperkt tot huidig fiscaal jaar

### Foutafhandeling

1. Netwerk Problemen
   - Automatische retry met exponentiële backoff
   - Maximum retry interval: 30 minuten
   - Terugval naar gecachte waarden indien beschikbaar

2. Data Validatie
   - Negatieve vermogenswaarden geaccepteerd (productie)
   - Spanningsbereik: 207V-253V (gefilterd)
   - Stroombereik: 0-100A (gefilterd)
   - Prijsbereik: 0-10 (valuta-eenheden, gefilterd)

3. Ontbrekende Data
   - Vermogensmetingen: Gemarkeerd als niet beschikbaar
   - Prijsgegevens: Gebruikt laatst bekende goede waarde
   - Accumulatie: Geïnterpoleerd vanaf geldige metingen
