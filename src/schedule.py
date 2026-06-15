"""
schedule.py
Reads and parses calendar.json to return today's events.
"""

import json
import os
from datetime import datetime, date


CALENDAR_FILE = os.path.join(os.path.dirname(__file__), "..", "calendar.json")


def load_events(filepath: str = CALENDAR_FILE) -> list:
    """Load all events from calendar.json."""
    try:
        with open(filepath, "r") as f:
            data = json.load(f)
        return data.get("events", [])
    except FileNotFoundError:
        raise FileNotFoundError(f"calendar.json not found at: {filepath}")
    except json.JSONDecodeError:
        raise ValueError("calendar.json is not valid JSON.")


def get_todays_events(events: list, target_date: date = None) -> list:
    """Filter events to only those occurring today (or target_date)."""
    if target_date is None:
        target_date = date.today()

    todays = []
    for event in events:
        try:
            start_dt = datetime.fromisoformat(event["start"])
            if start_dt.date() == target_date:
                todays.append({
                    "title": event.get("title", "Untitled"),
                    "start": start_dt,
                    "end": datetime.fromisoformat(event["end"]),
                    "location": event.get("location", "Unknown"),
                })
        except (KeyError, ValueError):
            continue

    return sorted(todays, key=lambda e: e["start"])


def format_event_time(event: dict) -> str:
    """Return a human-readable time string for an event."""
    start = event["start"].strftime("%I:%M %p")
    end = event["end"].strftime("%I:%M %p")
    return f"{start} – {end}"
