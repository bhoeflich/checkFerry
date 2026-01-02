# 🚢 Ferry Checker

Automatic monitoring of ferry availability on [meinefaehre.faehre.de](https://meinefaehre.faehre.de) (Wyker Dampfschiffs-Reederei Föhr-Amrum). The script regularly checks for available ferry connections **with vehicle transport** and sends a push notification via [ntfy.sh](https://ntfy.sh) upon success.

## ✨ Features

- 🔄 **Automatic Monitoring** – Continuously checks for availability
- 📅 **Multiple Dates** – Monitors any number of desired dates simultaneously
- ⏰ **Time Filter** – Only connections within a specific time range
- 🚗 **Vehicle Filter** – Ignores passenger-only ferries
- 🛣️ **Flexible Routes** – Any departure and arrival harbors configurable
- 📱 **Push Notifications** – Instant notification via ntfy.sh
- 🚀 **Startup Notification** – Confirms successful start of the service
- 🐳 **Docker-Ready** – Easy deployment as a container
- 🔧 **Programmable API** – `FerryService` as a reusable module

## 📋 Requirements

### Docker (Recommended)
- Docker Desktop or Docker Engine

### Local
- Python 3.10+
- Playwright with Chromium browser

## 🚀 Quick Start

### Docker

```bash
# Build image
docker build -t ferry-checker .

# Start container
docker run -d \
  -e TARGET_DATES="2026-01-02,2026-01-03" \
  -e NTFY_TOPIC="my-ferry-topic" \
  --name ferry-checker \
  ferry-checker
```

### Local

```bash
pip install -r requirements.txt
playwright install chromium

export TARGET_DATES="2026-01-02"
export NTFY_TOPIC="my-ferry-topic"
python main.py
```

## ⚙️ Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `TARGET_DATES` | Dates to check (YYYY-MM-DD) | `2026-01-02` | `2026-01-02,2026-01-03` |
| `NTFY_TOPIC` | ntfy.sh Topic Name | - | `my-ferry-topic` |
| `DEPARTURE` | Departure Harbor Code | `DEWYK` | `DEDAG` |
| `ARRIVAL` | Arrival Harbor Code | `DEDAG` | `DEWYK` |
| `TIME_FROM` | Earliest Departure | - | `08:00` |
| `TIME_TO` | Latest Departure | - | `18:00` |
| `CHECK_INTERVAL` | Check Interval (Seconds) | `300` | `600` |

### Harbor Codes

| Code | Harbor |
|------|--------|
| `DEWYK` | Wyk (Föhr) |
| `DEDAG` | Dagebüll |
| `DEWIT` | Wittdün (Amrum) |
| `DENOR` | Nordstrand |
| `DEPEL` | Pellworm |
| `DESCH` | Schlüttsiel |

## 🔧 FerryService API

The module `ferry_service.py` can also be used directly in Python:

```python
from ferry_service import check_ferry_availability, FerryService

# Simple function
connections = check_ferry_availability(
    departure="DEWYK",
    arrival="DEDAG",
    dates=["2026-01-02", "2026-01-03"],
    time_from="08:00",
    time_to="18:00"
)

for conn in connections:
    print(f"{conn.date} {conn.departure_time}: {conn.booking_url}")

# Or with Service class for more control
service = FerryService(headless=True)
all_connections = service.query(
    departure="DEDAG",
    arrival="DEWYK",
    dates=["2026-01-02"],
    only_available=False,  # All connections
    exclude_only_persons=True
)
```

### FerryConnection Object

```python
@dataclass
class FerryConnection:
    date: str              # "2026-01-02"
    departure_time: str    # "08:30"
    arrival_time: str      # "09:15"
    departure_harbor: str  # "DEWYK"
    arrival_harbor: str    # "DEDAG"
    available: bool        # True/False
    only_persons: bool     # True if "passengers only"
    booking_url: str       # Booking link
    raw_text: str          # Raw text of the connection
```

## 📱 Notifications

1. Install [ntfy App](https://ntfy.sh/)
2. Subscribe to topic (e.g., `my-ferry-topic`)
3. Set `NTFY_TOPIC`

## 🐳 Docker Commands

```bash
# Start with all options
docker run -d --name ferry-checker \
  -e TARGET_DATES="2026-01-02,2026-01-03" \
  -e DEPARTURE="DEDAG" \
  -e ARRIVAL="DEWYK" \
  -e TIME_FROM="08:00" \
  -e TIME_TO="18:00" \
  -e NTFY_TOPIC="my-topic" \
  -e CHECK_INTERVAL="600" \
  ferry-checker

# Show logs
docker logs -f ferry-checker

# Stop & Remove
docker stop ferry-checker && docker rm ferry-checker
```

## 📁 Project Structure

```
checkFerry/
├── ferry_service.py  # FerryService API Module
├── main.py           # Main script with monitoring loop
├── requirements.txt  # Python dependencies
├── Dockerfile
├── .dockerignore
└── README.md
```

## 📄 License

MIT
