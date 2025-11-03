# 🔧 Tibber Advanced v0.3.1 - Network Resilience Update

## ⚡ Wat is er gefixt?

### 🌐 **Verbeterde Netwerkstabiliteit**
- **Automatisch herstel** van tijdelijke verbindingsproblemen
- **Slimme reconnection** met exponential backoff (30s → 10min)
- **Geen handmatig herladen** meer nodig na netwerkproblemen

### 🚨 **Minder Valse Alarmen**
- Server onderhoud wordt niet meer als fatale fout gemeld
- Gateway timeouts (504) worden automatisch opnieuw geprobeerd
- Progressieve error logging: warnings eerst, echte errors later

### 🔄 **Betere Error Handling**
- HTML error pages tijdens outages correct afgehandeld
- 502/503/504 server errors nu retryable in plaats van fataal
- Automatische connection reset na 10 mislukte pogingen

---

## 📋 **Voor Wie is Deze Update?**

**✅ Je hebt deze update nodig als:**
- Je ziet regelmatig "Herverbinden met Tibber mislukt" meldingen
- Je integratie gaat offline tijdens Tibber server onderhoud
- Je krijgt "Unexpected content type: text/html" errors
- Je moet handmatig herladen na netwerkproblemen

**🎯 Resultaat na update:**
- **Stabielere verbinding** tijdens netwerk hiccups
- **Automatisch herstel** van tijdelijke problemen  
- **Minder notificaties** over tijdelijke issues
- **Betere uptime** van je prijssensoren

---

## ⚙️ **Installatie**

**Geen actie vereist** - dit is een maintenance update:
1. Update via HACS zoals gewoonlijk
2. Herstart Home Assistant 
3. Geniet van stabielere Tibber connectie!

**Alle configuratie blijft hetzelfde** als v0.3.0.

---

**Upgrade aanbevolen voor alle gebruikers!** 🚀