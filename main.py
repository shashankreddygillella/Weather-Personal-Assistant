"""
main.py
CLI entry point for the Weather-Aware Personal Assistant.
Orchestrates: weather fetch → schedule load → advice generation → display.
"""

import sys
import os

# Allow imports from src/
sys.path.insert(0, os.path.dirname(__file__))

from src.weather import fetch_weather, get_current_conditions, get_hourly_conditions
from src.schedule import load_events, get_todays_events
from src.advisor import build_full_report


def main():
    print("\n🔄 Fetching weather data for Houston, TX...")
    try:
        raw_weather = fetch_weather()
    except ConnectionError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    current = get_current_conditions(raw_weather)
    hourly = get_hourly_conditions(raw_weather)

    print("📅 Loading your schedule...")
    try:
        all_events = load_events()
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    todays_events = get_todays_events(all_events)

    report = build_full_report(todays_events, current, hourly)
    print("\n" + report)


if __name__ == "__main__":
    main()
