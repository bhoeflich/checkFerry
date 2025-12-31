# 🚢 Ferry Checker

Automatische Überwachung der Fährverfügbarkeit auf [meinefaehre.faehre.de](https://meinefaehre.faehre.de) (Wyker Dampfschiffs-Reederei Föhr-Amrum). Das Skript prüft regelmäßig auf freie Fährverbindungen **mit Fahrzeugmitnahme** und sendet bei Erfolg eine Push-Benachrichtigung via [ntfy.sh](https://ntfy.sh).

## ✨ Features

- 🔄 **Automatische Überwachung** – Prüft alle 5 Minuten auf Verfügbarkeit
- 📅 **Mehrere Daten** – Überwacht beliebig viele Wunschtermine gleichzeitig
- 🚗 **Fahrzeug-Filter** – Ignoriert reine Personenfähren ("Nur Personen")
- 📱 **Push-Benachrichtigungen** – Sofortige Benachrichtigung via ntfy.sh
- 🐳 **Docker-Ready** – Einfaches Deployment als Container

## 📋 Voraussetzungen

### Lokal
- Python 3.10+
- Playwright mit Chromium-Browser

### Docker
- Docker Desktop oder Docker Engine

## 🚀 Installation

### Option 1: Docker (Empfohlen)

```bash
# Image bauen
docker build -t ferry-checker .

# Container starten
docker run -d \
  -e TARGET_DATES="2026-01-02,2026-01-03" \
  -e NTFY_TOPIC="mein-faehren-topic" \
  --name ferry-checker \
  ferry-checker
```

### Option 2: Lokale Installation

```bash
# 1. Dependencies installieren
pip install -r requirements.txt

# 2. Playwright Browser installieren
playwright install chromium

# 3. Umgebungsvariablen setzen
export TARGET_DATES="2026-01-02,2026-01-03"
export NTFY_TOPIC="mein-faehren-topic"

# 4. Skript starten
python main.py
```

## ⚙️ Konfiguration

| Variable | Beschreibung | Beispiel |
|----------|--------------|----------|
| `TARGET_DATES` | Komma-separierte Liste der zu prüfenden Daten (YYYY-MM-DD) | `2026-01-02,2026-01-03` |
| `NTFY_TOPIC` | Dein eindeutiger ntfy.sh Topic-Name | `mein-faehren-topic` |

### Route

Aktuell ist die Route fest auf **Wyk (Föhr) → Dagebüll** eingestellt:
- Abfahrt: `DEWYK` (Wyk auf Föhr)
- Ankunft: `DEDAG` (Dagebüll)

Die Route kann in `main.py` unter `DEPARTURE` und `ARRIVAL` angepasst werden.

## 📱 Benachrichtigungen einrichten

1. Installiere die [ntfy App](https://ntfy.sh/) auf deinem Smartphone
2. Abonniere deinen gewählten Topic-Namen (z.B. `mein-faehren-topic`)
3. Setze `NTFY_TOPIC` auf denselben Namen

Bei Fund einer verfügbaren Verbindung erhältst du eine Push-Benachrichtigung mit direktem Link zur Buchung.

## 🔧 Docker-Befehle

```bash
# Container im Hintergrund starten
docker run -d --name ferry-checker \
  -e TARGET_DATES="2026-01-02" \
  -e NTFY_TOPIC="mein-topic" \
  ferry-checker

# Logs anzeigen
docker logs -f ferry-checker

# Container stoppen
docker stop ferry-checker

# Container entfernen
docker rm ferry-checker
```

## 📁 Projektstruktur

```
checkFerry/
├── main.py           # Hauptskript
├── requirements.txt  # Python-Abhängigkeiten
├── Dockerfile        # Docker-Konfiguration
├── .dockerignore     # Ausschlüsse für Docker-Build
└── README.md         # Diese Datei
```

## 🛠️ Funktionsweise

1. Das Skript startet einen headless Chromium-Browser via Playwright
2. Es ruft die Fahrplanseite für jeden konfigurierten Tag auf
3. Alle Verbindungen werden analysiert:
   - ✅ Verfügbar: "Auswählen"-Button vorhanden
   - ❌ Ignoriert: "Nur Personen" Verbindungen
4. Bei Treffer: Push-Benachrichtigung + Skript beendet sich
5. Bei keinem Treffer: 5 Minuten warten, dann erneut prüfen

## 📄 Lizenz

MIT
