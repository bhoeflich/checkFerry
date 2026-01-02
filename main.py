"""
Ferry Checker - Main Application
================================
Monitors ferry availability and sends notifications via ntfy.sh
"""

import os
import time
import argparse
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
    
    parser = argparse.ArgumentParser(description="Ferry Checker")
    parser.add_argument("--export-json", help="Path to export available connections as JSON", default=None)
    args = parser.parse_args()

    # Send startup notification with details (only if not exporting)
    if not args.export_json:
        time_info = f" ({TIME_FROM}-{TIME_TO})" if TIME_FROM or TIME_TO else ""
        dates_str = ", ".join(TARGET_DATES)
        send_notification(
            f"🚢 Ferry Checker started!\n"
            f"📅 Days: {dates_str}\n"
            f"⏰ Time Period: {TIME_FROM or '00:00'} - {TIME_TO or '23:59'}"
        )
    
    service = FerryService()
    notified_connections = set()
    
    # Single run mode for export
    if args.export_json:
        print(f"Running in export mode. Checking dates: {TARGET_DATES}")
        try:
            connections = service.find_available(
                departure=DEPARTURE,
                arrival=ARRIVAL,
                dates=TARGET_DATES,
                time_from=TIME_FROM,
                time_to=TIME_TO,
            )
            
            # Serialize
            data = []
            for conn in connections:
                data.append({
                    "date": conn.date,
                    "departure_time": conn.departure_time,
                    "arrival_time": conn.arrival_time,
                    "departure_harbor": conn.departure_harbor,
                    "arrival_harbor": conn.arrival_harbor,
                    "booking_url": conn.booking_url,
                    "available": conn.available
                })
            
            import json
            os.makedirs(os.path.dirname(args.export_json), exist_ok=True)
            with open(args.export_json, 'w', encoding='utf-8') as f:
                json.dump({"updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "connections": data}, f, indent=2)
            
            print(f"Exported {len(data)} connections to {args.export_json}")
            return # Exit after one run
            
        except Exception as e:
            print(f"Error during export: {e}")
            return

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
                print(f"✅ SUCCESS: {len(connections)} connection(s) found!")
                
                for conn in connections:
                    # Create unique identifier for the connection
                    conn_id = (conn.date, conn.departure_time, conn.departure_harbor, conn.arrival_harbor)
                    
                    if conn_id not in notified_connections:
                        message = (
                            f"🚢 Ferry Found!\n"
                            f"Date: {conn.date}\n"
                            f"Time: {conn.departure_time}\n"
                            f"Link: {conn.booking_url}"
                        )
                        print(f"   Existing connection found: {conn.date} at {conn.departure_time}")
                        print("   -> Sending notification...")
                        send_notification(message)
                        notified_connections.add(conn_id)
                    else:
                        print(f"   Skipping already notified connection: {conn.date} at {conn.departure_time}")
            else:
                print("❌ No available connections found.")
                
        except Exception as e:
            print(f"⚠️ Error during check: {e}")
        
        print(f"Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    main()
