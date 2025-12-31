# 🚢 Ferry Checker

Automatische Überwachung der Fährverfügbarkeit auf [meinefaehre.faehre.de](https://meinefaehre.faehre.de) (Wyker Dampfschiffs-Reederei Föhr-Amrum). Das Skript prüft regelmäßig auf freie Fährverbindungen **mit Fahrzeugmitnahme** und sendet bei Erfolg eine Push-Benachrichtigung via [ntfy.sh](https://ntfy.sh).

## ✨ Features

- 🔄 **Automatische Überwachung** – Prüft kontinuierlich auf Verfügbarkeit
- 📅 **Mehrere Daten** – Überwacht beliebig viele Wunschtermine gleichzeitig
- ⏰ **Zeitfilter** – Nur Verbindungen in einem bestimmten Zeitraum
- 🚗 **Fahrzeug-Filter** – Ignoriert reine Personenfähren
- 🛣️ **Flexible Routen** – Beliebige Start- und Zielhäfen konfigurierbar
- 📱 **Push-Benachrichtigungen** – Sofortige Benachrichtigung via ntfy.sh
- 🐳 **Docker-Ready** – Einfaches Deployment als Container
- 🔧 **Programmierbare API** – `FerryService` als wiederverwendbares Modul

## 📋 Voraussetzungen

### Docker (Empfohlen)
- Docker Desktop oder Docker Engine

### Lokal
- Python 3.10+
- Playwright mit Chromium-Browser

## 🚀 Schnellstart

### Docker

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

### Lokal

```bash
pip install -r requirements.txt
playwright install chromium

export TARGET_DATES="2026-01-02"
export NTFY_TOPIC="mein-faehren-topic"
python main.py
```

## ⚙️ Konfiguration

| Variable | Beschreibung | Standard | Beispiel |
|----------|--------------|----------|----------|
| `TARGET_DATES` | Zu prüfende Daten (YYYY-MM-DD) | `2026-01-02` | `2026-01-02,2026-01-03` |
| `NTFY_TOPIC` | ntfy.sh Topic-Name | - | `mein-faehren-topic` |
| `DEPARTURE` | Abfahrtshafen-Code | `DEWYK` | `DEDAG` |
| `ARRIVAL` | Zielhafen-Code | `DEDAG` | `DEWYK` |
| `TIME_FROM` | Früheste Abfahrt | - | `08:00` |
| `TIME_TO` | Späteste Abfahrt | - | `18:00` |
| `CHECK_INTERVAL` | Prüfintervall (Sekunden) | `300` | `600` |

### Hafencodes

| Code | Hafen |
|------|-------|
| `DEWYK` | Wyk (Föhr) |
| `DEDAG` | Dagebüll |
| `DEWIT` | Wittdün (Amrum) |
| `DENOR` | Nordstrand |
| `DEPEL` | Pellworm |
| `DESCH` | Schlüttsiel |

## 🔧 FerryService API

Das Modul `ferry_service.py` kann auch direkt in Python verwendet werden:

```python
from ferry_service import check_ferry_availability, FerryService

# Einfache Funktion
connections = check_ferry_availability(
    departure="DEWYK",
    arrival="DEDAG",
    dates=["2026-01-02", "2026-01-03"],
    time_from="08:00",
    time_to="18:00"
)

for conn in connections:
    print(f"{conn.date} {conn.departure_time}: {conn.booking_url}")

# Oder mit Service-Klasse für mehr Kontrolle
service = FerryService(headless=True)
all_connections = service.query(
    departure="DEDAG",
    arrival="DEWYK",
    dates=["2026-01-02"],
    only_available=False,  # Alle Verbindungen
    exclude_only_persons=True
)
```

### FerryConnection Objekt

```python
@dataclass
class FerryConnection:
    date: str              # "2026-01-02"
    departure_time: str    # "08:30"
    arrival_time: str      # "09:15"
    departure_harbor: str  # "DEWYK"
    arrival_harbor: str    # "DEDAG"
    available: bool        # True/False
    only_persons: bool     # True wenn "Nur Personen"
    booking_url: str       # Link zur Buchung
    raw_text: str          # Roher Text der Verbindung
```

## 📱 Benachrichtigungen

1. [ntfy App](https://ntfy.sh/) installieren
2. Topic abonnieren (z.B. `mein-faehren-topic`)
3. `NTFY_TOPIC` setzen

## 🐳 Docker-Befehle

```bash
# Mit allen Optionen starten
docker run -d --name ferry-checker \
  -e TARGET_DATES="2026-01-02,2026-01-03" \
  -e DEPARTURE="DEDAG" \
  -e ARRIVAL="DEWYK" \
  -e TIME_FROM="08:00" \
  -e TIME_TO="18:00" \
  -e NTFY_TOPIC="mein-topic" \
  -e CHECK_INTERVAL="600" \
  ferry-checker

# Logs anzeigen
docker logs -f ferry-checker

# Stoppen & Entfernen
docker stop ferry-checker && docker rm ferry-checker
```

## 📁 Projektstruktur

```
checkFerry/
├── ferry_service.py  # FerryService API-Modul
├── main.py           # Hauptskript mit Monitoring-Loop
├── requirements.txt  # Python-Abhängigkeiten
├── Dockerfile
├── .dockerignore
└── README.md
```

## 📄 Lizenz

MIT
