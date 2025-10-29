# Contributing to Tibber Advanced

Bedankt voor je interesse in het bijdragen aan Tibber Advanced! 🎉

## 🐛 Bug Reports

Als je een bug vindt, maak dan een [issue](https://github.com/OdynBrouwer/HomeAssistantTibber/issues/new?template=bug_report.md) aan met:
- Duidelijke beschrijving van het probleem
- Stappen om te reproduceren
- Home Assistant versie
- Relevante logs

## 💡 Feature Requests

Heb je een idee? Maak een [feature request](https://github.com/OdynBrouwer/HomeAssistantTibber/issues/new?template=feature_request.md) aan!

## 🔧 Pull Requests

### Voordat je begint
1. Fork de repository
2. Clone je fork: `git clone https://github.com/jouw-username/HomeAssistantTibber.git`
3. Maak een nieuwe branch (`git checkout -b feature/mijn-feature`)
4. **Let op**: Test lokaal in de juiste folder structuur:
   ```
   /config/custom_components/tibber_adv/    ← Niet HomeAssistantTibber!
   ```
   De repository heet `HomeAssistantTibber`, maar moet geïnstalleerd worden als `tibber_adv`
5. Test je wijzigingen lokaal

### Code Style
- Volg [PEP 8](https://www.python.org/dev/peps/pep-0008/) voor Python code
- Gebruik type hints waar mogelijk
- Voeg docstrings toe aan functies en classes
- Houd regels onder 100 karakters

### Commit Messages
- Gebruik duidelijke, beschrijvende commit messages
- Begin met een werkwoord: "Add", "Fix", "Update", "Remove"
- Bijvoorbeeld: "Fix currency fallback for RT sensors"

### Testing
- Test je wijzigingen met een echte Tibber account
- Controleer of alle sensors correct werken
- Verifieer dat de configuratie correct wordt opgeslagen

### Documentation
- Update README.md als je features toevoegt
- Voeg voorbeelden toe aan `/examples` als relevant
- Update CHANGELOG.md met je wijzigingen
- Zorg dat comments in het Nederlands of Engels zijn

## 📝 Translations

We verwelkomen vertalingen! Voeg een nieuwe taal toe door:
1. Kopieer `translations/en.json`
2. Vertaal alle strings
3. Test de vertaling in Home Assistant
4. Stuur een PR

## 🌍 Dutch Market Specifics

Bij het werken aan Nederlandse functionaliteit:
- Gebruik de juiste belastingtarieven (EB, ODE, BTW)
- Houd rekening met salderingsregels
- Test met negatieve prijzen (komt voor in NL)
- Documenteer in het Nederlands in README.md

## 🎯 Areas for Contribution

Ideeën waar we hulp bij kunnen gebruiken:
- Verbeterde dashboard voorbeelden
- Meer automation templates
- Ondersteuning voor andere markten (Zweden, Noorwegen, Duitsland)
- Testcoverage verbeteren
- Performance optimalisaties

## ❓ Vragen?

Open een [discussion](https://github.com/OdynBrouwer/HomeAssistantTibber/discussions) of maak een issue aan!

## 📜 License

Door bij te dragen ga je akkoord dat je bijdragen onder dezelfde [MIT License](LICENSE) vallen.
