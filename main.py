import os
import time
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright

# Configuration
# Ensure these environment variables are set
NTFY_TOPIC = os.environ.get("NTFY_TOPIC")
TARGET_DATES_STR = os.environ.get("TARGET_DATES", "2026-01-02")
TARGET_DATES = [d.strip() for d in TARGET_DATES_STR.split(",") if d.strip()]

BASE_URL = "https://meinefaehre.faehre.de/fahrplanauskunft"
DEPARTURE = "DEWYK"
ARRIVAL = "DEDAG"

def send_notification(message):
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

def check_ferry(date):
    """Checks the ferry website for availability on a specific date."""
    url = f"{BASE_URL}?departure_harbor={DEPARTURE}&arrival_harbor={ARRIVAL}&date={date}"
    
    with sync_playwright() as p:
        # Launch browser (headless=True for background execution)
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        
        print(f"Checking {date}...")
        
        try:
            page.goto(url, timeout=60000)
            
            # Wait for the schedule to load.
            try:
                page.wait_for_selector(".time.list-record", state="attached", timeout=30000)
            except Exception:
                print(f"  [{date}] No connections found or timeout.")
                return False

            connections = page.query_selector_all(".time.list-record")
            print(f"  [{date}] Found {len(connections)} connections.")

            for conn in connections:
                text = conn.inner_text()
                
                button = conn.query_selector("button.btn-red")
                has_button = button is not None and button.is_visible()
                
                is_only_persons = "nur personen" in text.lower()
                has_select_text = "AUSWÄHLEN" in text.upper()

                if (has_button or has_select_text) and not is_only_persons:
                    print(f"  [{date}] SUCCESS: Available connection found! {text.replace(chr(10), ' ')}")
                    return url
            
            return False

        except Exception as e:
            print(f"  [{date}] Error: {e}")
            return False
        finally:
            browser.close()

def main():
    print("Starting Ferry Checker App...")
    print(f"Target Dates: {TARGET_DATES}")
    if not NTFY_TOPIC:
        print("WARNING: NTFY_TOPIC is not set. Notifications will not be sent.")
    print("Press Ctrl+C to stop.")
    
    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"\n[{timestamp}] Starting check cycle...")
        
        found_any = False
        
        for date in TARGET_DATES:
            result_url = check_ferry(date)
            if result_url:
                send_notification(f"Ferry Found on {date}! Link: {result_url}")
                found_any = True
                break # Exit dates loop
        
        if found_any:
            print("Found a connection! Exiting.")
            break
        
        print("Cycle match not found. Sleeping for 5 minutes...")
        time.sleep(300)

if __name__ == "__main__":
    main()
