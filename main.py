"""
Ferry Checker - Main Application
================================
Monitors ferry availability and sends notifications via ntfy.sh
"""

import os
import time
from datetime import datetime

import requests
from ferry_service import FerryService, check_ferry_availability, HARBORS


# Configuration from environment variables
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
TARGET_DATES_STR = os.environ.get("TARGET_DATES", "2026-01-02")
TARGET_DATES = [d.strip() for d in TARGET_DATES_STR.split(",") if d.strip()]

# Route configuration
DEPARTURE = os.environ.get("DEPARTURE", "DEWYK")
ARRIVAL = os.environ.get("ARRIVAL", "DEDAG")

# Time range filter (optional)
TIME_FROM = os.environ.get("TIME_FROM")  # e.g., "08:00"
TIME_TO = os.environ.get("TIME_TO")      # e.g., "18:00"

# Check interval in seconds (default: 5 minutes)
CHECK_INTERVAL = int(os.environ.get("CHECK_INTERVAL", "300"))


def send_notification(message: str) -> None:
    """Sends a push notification using ntfy.sh."""
    if not NTFY_TOPIC:
        print("NTFY_TOPIC not set. Skipping notification.")
        print(f"Would have sent: {message}")
        return

    try:
        requests.post(
            f"https://ntfy.sh/{NTFY_TOPIC}",
            data=message.encode(encoding='utf-8'),
            headers={"Title": "Ferry Checker Alert", "Priority": "high"}
        )
        print("Notification sent via ntfy.sh")
    except Exception as e:
        print(f"Failed to send notification: {e}")


def main():
    """Main loop for continuous ferry checking."""
    print("=" * 50)
    print("🚢 Starting Ferry Checker App...")
    print("=" * 50)
    print(f"Route: {HARBORS.get(DEPARTURE, DEPARTURE)} → {HARBORS.get(ARRIVAL, ARRIVAL)}")
    print(f"Target Dates: {TARGET_DATES}")
    if TIME_FROM or TIME_TO:
        print(f"Time Filter: {TIME_FROM or '00:00'} - {TIME_TO or '23:59'}")
    if not NTFY_TOPIC:
        print("⚠️  WARNING: NTFY_TOPIC is not set. Notifications will not be sent.")
    print(f"Check Interval: {CHECK_INTERVAL} seconds")
    print("Press Ctrl+C to stop.")
    print("=" * 50)
    
    service = FerryService()
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Starting check cycle...")
        
        try:
            connections = service.find_available(
                departure=DEPARTURE,
                arrival=ARRIVAL,
                dates=TARGET_DATES,
                time_from=TIME_FROM,
                time_to=TIME_TO,
            )
            
            if connections:
                conn = connections[0]
                message = (
                    f"🚢 Ferry Found!\n"
                    f"Date: {conn.date}\n"
                    f"Time: {conn.departure_time}\n"
                    f"Link: {conn.booking_url}"
                )
                print(f"✅ SUCCESS: {len(connections)} connection(s) found!")
                print(f"   First: {conn.date} at {conn.departure_time}")
                send_notification(message)
                print("Found a connection! Exiting.")
                break
            else:
                print("❌ No available connections found.")
                
        except Exception as e:
            print(f"⚠️ Error during check: {e}")
        
        print(f"Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
