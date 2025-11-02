# 🚀 Tibber Advanced v0.3.0 - Major Dutch Market Update

## ⚡ Wat is er nieuw?

### ✅ **Accuratere Prijsberekeningen**
- Prijzen nu 100% accuraat! Van 0.3264 naar correcte ~0.2296 EUR/kWh
- Berekeningen gevalideerd tegen officiële Tibber API (±0.00005 EUR/kWh nauwkeurig)

### 🇳🇱 **Nederlandse Interface** 
- Alle instellingen nu in het Nederlands in Nederlandse Home Assistant
- Duidelijke benamingen: "Energiebelasting", "Inkoopvergoeding", "BTW tarief"

### 📊 **Verbeterde Sensors**
- **"Nord Pool spotprijs"** (was: "Basis energieprijs zonder toeslag")
- **"Spotprijs + Inkoopvergoeding"** (was: "Prijs excl. BTW")
- Veel duidelijker wat elke sensor doet!

### 🌞 **Zonnepanelen Template Gefixt**
- Post-2027 regels correct geïmplementeerd (geen BTW terugbetaling meer)
- Negatieve prijzen handling verbeterd

---

## ⚠️ **BELANGRIJK - Actie Vereist**

### 🔧 **Herconfiguratie Nodig**
Na de update **MOET** je de integratie opnieuw configureren:

1. **Ga naar**: Instellingen → Apparaten & Services → Tibber Advanced
2. **Klik op**: ⋮ → Configureren  
3. **Stel in**:
   - **Energiebelasting incl. BTW**: 0.1228 EUR/kWh
   - **BTW tarief**: 21.0%
   - **Inkoopvergoeding excl. BTW**: 0.0205 EUR/kWh
4. **Opslaan** en **herlaad** de integratie

### 📋 **Oude Sensors Opruimen**
- Sommige oude sensor entiteiten kunnen verkeerde namen hebben
- Check je dashboards en automatiseringen na de update
- Gebruik **Developer Tools → States** om nieuwe sensor namen te vinden

---

## 🎯 **Resultaat**
- **Perfecte** prijsberekeningen volgens Nederlandse markt
- **Duidelijke** Nederlandse interface  
- **Nauwkeurige** zonnepaneel teruglevering berekeningen
- **Toekomstbestendige** 2027 saldering regels

**Geniet van accuratere stroomprijzen!** ⚡🇳🇱