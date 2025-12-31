"""
Ferry Service Module
====================
Reusable service for querying ferry availability on meinefaehre.faehre.de
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from playwright.sync_api import sync_playwright


# Known harbor codes
HARBORS = {
    "DEWYK": "Wyk (Föhr)",
    "DEDAG": "Dagebüll",
    "DEWIT": "Wittdün (Amrum)",
    "DENOR": "Nordstrand",
    "DEPEL": "Pellworm",
    "DESCH": "Schlüttsiel",
}

BASE_URL = "https://meinefaehre.faehre.de/fahrplanauskunft"


@dataclass
class FerryConnection:
    """Represents a single ferry connection."""
    date: str
    departure_time: str
    arrival_time: str
    departure_harbor: str
    arrival_harbor: str
    available: bool
    only_persons: bool
    booking_url: str
    raw_text: str


class FerryService:
    """Service for querying ferry availability."""

    def __init__(self, headless: bool = True):
        """
        Initialize the FerryService.
        
        Args:
            headless: Run browser in headless mode (default: True)
        """
        self.headless = headless

    def query(
        self,
        departure: str,
        arrival: str,
        dates: list[str],
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        only_available: bool = False,
        exclude_only_persons: bool = True,
    ) -> list[FerryConnection]:
        """
        Query ferry connections for given parameters.
        
        Args:
            departure: Departure harbor code (e.g., "DEWYK")
            arrival: Arrival harbor code (e.g., "DEDAG")
            dates: List of dates to check (format: "YYYY-MM-DD")
            time_from: Optional start time filter (format: "HH:MM")
            time_to: Optional end time filter (format: "HH:MM")
            only_available: If True, only return available connections
            exclude_only_persons: If True, exclude "Nur Personen" connections
            
        Returns:
            List of FerryConnection objects
        """
        all_connections = []

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=self.headless)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                           "AppleWebKit/537.36 (KHTML, like Gecko) "
                           "Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            try:
                for date in dates:
                    connections = self._query_date(
                        page, departure, arrival, date,
                        time_from, time_to, only_available, exclude_only_persons
                    )
                    all_connections.extend(connections)
            finally:
                browser.close()

        return all_connections

    def _query_date(
        self,
        page,
        departure: str,
        arrival: str,
        date: str,
        time_from: Optional[str],
        time_to: Optional[str],
        only_available: bool,
        exclude_only_persons: bool,
    ) -> list[FerryConnection]:
        """Query connections for a single date."""
        url = f"{BASE_URL}?departure_harbor={departure}&arrival_harbor={arrival}&date={date}"
        connections = []

        try:
            page.goto(url, timeout=60000)
            
            # Wait for schedule to load
            try:
                page.wait_for_selector(".time.list-record", state="attached", timeout=30000)
            except Exception:
                return connections

            records = page.query_selector_all(".time.list-record")

            for record in records:
                connection = self._parse_connection(record, date, departure, arrival, url)
                if connection is None:
                    continue
                    
                # Apply filters
                if only_available and not connection.available:
                    continue
                if exclude_only_persons and connection.only_persons:
                    continue
                if time_from and connection.departure_time < time_from:
                    continue
                if time_to and connection.departure_time > time_to:
                    continue
                    
                connections.append(connection)

        except Exception as e:
            print(f"Error querying {date}: {e}")

        return connections

    def _parse_connection(
        self, record, date: str, departure: str, arrival: str, url: str
    ) -> Optional[FerryConnection]:
        """Parse a connection record from the page."""
        try:
            text = record.inner_text()
            
            # Extract times from text (format varies, try common patterns)
            departure_time = ""
            arrival_time = ""
            
            # Look for time elements
            time_elements = record.query_selector_all(".departure-time, .arrival-time, .time-value")
            times_found = []
            for elem in time_elements:
                t = elem.inner_text().strip()
                if ":" in t and len(t) == 5:
                    times_found.append(t)
            
            if len(times_found) >= 2:
                departure_time = times_found[0]
                arrival_time = times_found[1]
            else:
                # Fallback: try to extract from text
                import re
                time_pattern = r'\b(\d{2}:\d{2})\b'
                matches = re.findall(time_pattern, text)
                if len(matches) >= 2:
                    departure_time = matches[0]
                    arrival_time = matches[1]
                elif len(matches) == 1:
                    departure_time = matches[0]

            # Check availability
            button = record.query_selector("button.btn-red")
            has_button = button is not None and button.is_visible()
            has_select_text = "AUSWÄHLEN" in text.upper()
            available = has_button or has_select_text
            
            only_persons = "nur personen" in text.lower()

            return FerryConnection(
                date=date,
                departure_time=departure_time,
                arrival_time=arrival_time,
                departure_harbor=departure,
                arrival_harbor=arrival,
                available=available,
                only_persons=only_persons,
                booking_url=url,
                raw_text=text.replace("\n", " ").strip(),
            )
        except Exception:
            return None

    def find_available(
        self,
        departure: str,
        arrival: str,
        dates: list[str],
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
    ) -> list[FerryConnection]:
        """
        Convenience method to find only available connections with vehicles.
        
        Args:
            departure: Departure harbor code
            arrival: Arrival harbor code
            dates: List of dates to check
            time_from: Optional start time filter
            time_to: Optional end time filter
            
        Returns:
            List of available FerryConnection objects (excluding "Nur Personen")
        """
        return self.query(
            departure=departure,
            arrival=arrival,
            dates=dates,
            time_from=time_from,
            time_to=time_to,
            only_available=True,
            exclude_only_persons=True,
        )


def check_ferry_availability(
    departure: str = "DEWYK",
    arrival: str = "DEDAG",
    dates: list[str] = None,
    time_from: str = None,
    time_to: str = None,
) -> list[FerryConnection]:
    """
    Standalone function to check ferry availability.
    
    Args:
        departure: Departure harbor code (default: "DEWYK" = Wyk)
        arrival: Arrival harbor code (default: "DEDAG" = Dagebüll)
        dates: List of dates to check (default: today)
        time_from: Optional start time filter (format: "HH:MM")
        time_to: Optional end time filter (format: "HH:MM")
        
    Returns:
        List of available FerryConnection objects
        
    Example:
        >>> connections = check_ferry_availability(
        ...     departure="DEWYK",
        ...     arrival="DEDAG",
        ...     dates=["2026-01-02", "2026-01-03"],
        ...     time_from="08:00",
        ...     time_to="18:00"
        ... )
        >>> for conn in connections:
        ...     print(f"{conn.date} {conn.departure_time}: Available!")
    """
    if dates is None:
        dates = [datetime.now().strftime("%Y-%m-%d")]
    
    service = FerryService()
    return service.find_available(
        departure=departure,
        arrival=arrival,
        dates=dates,
        time_from=time_from,
        time_to=time_to,
    )
