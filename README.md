# Ferry Checker

This Python application checks `meinefaehre.faehre.de` for ferry availability on 2026-01-02. If a slot for vehicles (not just persons) is found, it sends an SMS via Twilio.

## Prerequisites

- Python 3.7+
- A preferred `ntfy.sh` topic name (e.g., `my_ferry_check_123`)

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Install Browsers for Playwright:**
    ```bash
    playwright install chromium
    ```

3.  **Environment Variables:**
    Set the following environment variables.

    ```bash
    # Comma-separated list of dates to check (YYYY-MM-DD)
    export TARGET_DATES="2026-01-02,2026-01-03"
    
    # Your unique ntfy.sh topic
    export NTFY_TOPIC="your_unique_topic_name"
    ```

## Usage

Run the script:

```bash
python main.py
```

The script will:
1.  Launch a headless browser.
2.  Loop through each date in `TARGET_DATES`.
3.  If a valid connection ("Auswählen" available, not "Nur Personen") is found for ANY date:
    - Send a push notification via ntfy.sh.
    - Exit.
4.  If nothing found, sleep for 5 minutes and repeat.
