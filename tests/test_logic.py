"""
tests/test_logic.py
Automated tests for the Weather-Aware Personal Assistant core logic.

Coverage:
  - Weather condition classifiers (is_raining, is_stormy, is_hot, is_cold, is_windy)
  - Outdoor event heuristic detection
  - Advice generation for all rule branches
  - Schedule filtering and formatting
  - Full report generation

Run with:
    python -m pytest tests/ -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import datetime, date
from src.advisor import (
    is_raining, is_stormy, is_hot, is_cold, is_windy,
    is_outdoor_event, generate_advice, build_full_report,
    RAIN_CODE_MIN, STORM_CODE_MIN, HIGH_TEMP_F, LOW_TEMP_F,
    HIGH_WIND_MPH, HIGH_PRECIP_PROB,
)
from src.schedule import get_todays_events, format_event_time


# ── Shared Fixtures ───────────────────────────────────────────

CURRENT_RAIN = {
    "temperature": 72, "precipitation": 0.5, "windspeed": 15,
    "weathercode": 63, "description": "Rain", "city": "Houston, TX",
}
CURRENT_CLEAR = {
    "temperature": 80, "precipitation": 0.0, "windspeed": 8,
    "weathercode": 0, "description": "Clear sky", "city": "Houston, TX",
}
CURRENT_STORM = {
    "temperature": 75, "precipitation": 1.2, "windspeed": 30,
    "weathercode": 95, "description": "Thunderstorm", "city": "Houston, TX",
}
CURRENT_HOT = {
    "temperature": 98, "precipitation": 0.0, "windspeed": 5,
    "weathercode": 1, "description": "Mainly clear", "city": "Houston, TX",
}
CURRENT_COLD = {
    "temperature": 40, "precipitation": 0.0, "windspeed": 10,
    "weathercode": 0, "description": "Clear sky", "city": "Houston, TX",
}
CURRENT_WINDY = {
    "temperature": 70, "precipitation": 0.0, "windspeed": 30,
    "weathercode": 0, "description": "Clear sky", "city": "Houston, TX",
}
CURRENT_HIGH_PRECIP_PROB = {
    "temperature": 78, "precipitation": 0.0, "windspeed": 10,
    "weathercode": 2, "description": "Partly cloudy", "city": "Houston, TX",
}

EVENT_OUTDOOR = {
    "title": "Client Site Visit",
    "start": datetime(2026, 6, 15, 11, 0),
    "end": datetime(2026, 6, 15, 13, 0),
    "location": "Houston, TX",
}
EVENT_INDOOR = {
    "title": "Project Review Meeting",
    "start": datetime(2026, 6, 15, 15, 0),
    "end": datetime(2026, 6, 15, 16, 30),
    "location": "Houston, TX",
}
EVENT_GYM = {
    "title": "Evening Gym Session",
    "start": datetime(2026, 6, 15, 18, 0),
    "end": datetime(2026, 6, 15, 19, 30),
    "location": "Houston, TX",
}

# Hourly with 60% precip probability at 3pm — no rain code
HOURLY_HIGH_PROB = [
    {
        "time": "2026-06-15T15:00",
        "temperature": 78,
        "precipitation_probability": 60,
        "weathercode": 2,
        "description": "Partly cloudy",
    }
]
HOURLY_EMPTY = []  # Forces fallback to current conditions


# ── 1. Weather Condition Classifiers ─────────────────────────

class TestWeatherClassifiers:
    def test_is_raining_at_boundary(self):
        assert is_raining(RAIN_CODE_MIN) is True

    def test_is_raining_above_boundary(self):
        assert is_raining(63) is True

    def test_is_raining_below_boundary(self):
        assert is_raining(RAIN_CODE_MIN - 1) is False

    def test_is_raining_clear_sky(self):
        assert is_raining(0) is False

    def test_is_stormy_at_boundary(self):
        assert is_stormy(STORM_CODE_MIN) is True

    def test_is_stormy_above_boundary(self):
        assert is_stormy(99) is True

    def test_is_stormy_below_boundary(self):
        assert is_stormy(STORM_CODE_MIN - 1) is False

    def test_is_hot_at_boundary(self):
        assert is_hot(HIGH_TEMP_F) is True

    def test_is_hot_below_boundary(self):
        assert is_hot(HIGH_TEMP_F - 1) is False

    def test_is_hot_none_safe(self):
        assert is_hot(None) is False

    def test_is_cold_at_boundary(self):
        assert is_cold(LOW_TEMP_F) is True

    def test_is_cold_above_boundary(self):
        assert is_cold(LOW_TEMP_F + 1) is False

    def test_is_cold_none_safe(self):
        assert is_cold(None) is False

    def test_is_windy_at_boundary(self):
        assert is_windy(HIGH_WIND_MPH) is True

    def test_is_windy_below_boundary(self):
        assert is_windy(HIGH_WIND_MPH - 1) is False

    def test_is_windy_none_safe(self):
        assert is_windy(None) is False


# ── 2. Outdoor Event Detection ────────────────────────────────

class TestOutdoorDetection:
    def test_site_keyword_flagged(self):
        assert is_outdoor_event(EVENT_OUTDOOR) is True  # contains "site"

    def test_gym_keyword_flagged(self):
        assert is_outdoor_event(EVENT_GYM) is True  # contains "gym"

    def test_indoor_meeting_not_flagged(self):
        assert is_outdoor_event(EVENT_INDOOR) is False

    def test_run_keyword_flagged(self):
        event = {"title": "Morning Run", "start": datetime(2026, 6, 15, 7, 0),
                 "end": datetime(2026, 6, 15, 8, 0), "location": "Houston"}
        assert is_outdoor_event(event) is True

    def test_walk_keyword_flagged(self):
        event = {"title": "Evening Walk", "start": datetime(2026, 6, 15, 19, 0),
                 "end": datetime(2026, 6, 15, 20, 0), "location": "Houston"}
        assert is_outdoor_event(event) is True

    def test_case_insensitive(self):
        event = {"title": "SITE INSPECTION", "start": datetime(2026, 6, 15, 10, 0),
                 "end": datetime(2026, 6, 15, 11, 0), "location": "Houston"}
        assert is_outdoor_event(event) is True


# ── 3. Advice Generation ──────────────────────────────────────

class TestAdviceGeneration:
    def test_rain_triggers_umbrella_advice(self):
        advice = generate_advice(EVENT_INDOOR, CURRENT_RAIN, HOURLY_EMPTY)
        combined = " ".join(advice).lower()
        assert "umbrella" in combined or "rain" in combined

    def test_storm_triggers_reschedule_warning(self):
        advice = generate_advice(EVENT_OUTDOOR, CURRENT_STORM, HOURLY_EMPTY)
        combined = " ".join(advice).lower()
        assert "storm" in combined or "reschedul" in combined

    def test_clear_weather_gives_all_clear_checkmark(self):
        advice = generate_advice(EVENT_INDOOR, CURRENT_CLEAR, HOURLY_EMPTY)
        assert any("✅" in a for a in advice)

    def test_hot_weather_mentions_hydration_or_clothing(self):
        advice = generate_advice(EVENT_OUTDOOR, CURRENT_HOT, HOURLY_EMPTY)
        combined = " ".join(advice).lower()
        assert "hydrat" in combined or "light clothing" in combined

    def test_cold_weather_suggests_jacket(self):
        advice = generate_advice(EVENT_OUTDOOR, CURRENT_COLD, HOURLY_EMPTY)
        combined = " ".join(advice).lower()
        assert "jacket" in combined

    def test_windy_conditions_flag_loose_items(self):
        advice = generate_advice(EVENT_OUTDOOR, CURRENT_WINDY, HOURLY_EMPTY)
        combined = " ".join(advice).lower()
        assert "wind" in combined or "loose" in combined

    def test_outdoor_event_plus_rain_gives_extra_warning(self):
        advice = generate_advice(EVENT_OUTDOOR, CURRENT_RAIN, HOURLY_EMPTY)
        combined = " ".join(advice).lower()
        assert "outdoor" in combined or "rain gear" in combined

    def test_indoor_event_rain_no_outdoor_warning(self):
        advice = generate_advice(EVENT_INDOOR, CURRENT_RAIN, HOURLY_EMPTY)
        combined = " ".join(advice).lower()
        assert "outdoor" not in combined

    def test_high_precip_prob_via_hourly_triggers_umbrella(self):
        advice = generate_advice(EVENT_INDOOR, CURRENT_HIGH_PRECIP_PROB, HOURLY_HIGH_PROB)
        combined = " ".join(advice).lower()
        assert "umbrella" in combined or "rain" in combined

    def test_storm_advice_is_not_empty(self):
        advice = generate_advice(EVENT_OUTDOOR, CURRENT_STORM, HOURLY_EMPTY)
        assert len(advice) > 0

    def test_all_clear_is_only_advice_for_clear_indoor(self):
        advice = generate_advice(EVENT_INDOOR, CURRENT_CLEAR, HOURLY_EMPTY)
        assert len(advice) == 1
        assert "✅" in advice[0]

    def test_advice_references_event_title(self):
        advice = generate_advice(EVENT_OUTDOOR, CURRENT_RAIN, HOURLY_EMPTY)
        combined = " ".join(advice)
        assert "Client Site Visit" in combined


# ── 4. Schedule Logic ─────────────────────────────────────────

class TestScheduleLogic:
    def test_filters_to_target_date_only(self):
        events_raw = [
            {"title": "Meeting A", "start": "2026-06-15T09:00:00",
             "end": "2026-06-15T10:00:00", "location": "Houston"},
            {"title": "Meeting B", "start": "2026-06-16T09:00:00",
             "end": "2026-06-16T10:00:00", "location": "Houston"},
        ]
        result = get_todays_events(events_raw, target_date=date(2026, 6, 15))
        assert len(result) == 1
        assert result[0]["title"] == "Meeting A"

    def test_returns_empty_list_when_no_matching_events(self):
        events_raw = [
            {"title": "Future Event", "start": "2026-12-01T09:00:00",
             "end": "2026-12-01T10:00:00", "location": "Houston"},
        ]
        result = get_todays_events(events_raw, target_date=date(2026, 6, 15))
        assert result == []

    def test_events_sorted_by_start_time(self):
        events_raw = [
            {"title": "Late Meeting", "start": "2026-06-15T15:00:00",
             "end": "2026-06-15T16:00:00", "location": "Houston"},
            {"title": "Early Meeting", "start": "2026-06-15T09:00:00",
             "end": "2026-06-15T10:00:00", "location": "Houston"},
        ]
        result = get_todays_events(events_raw, target_date=date(2026, 6, 15))
        assert result[0]["title"] == "Early Meeting"
        assert result[1]["title"] == "Late Meeting"

    def test_skips_malformed_events_without_crashing(self):
        events_raw = [
            {"title": "Good Event", "start": "2026-06-15T09:00:00",
             "end": "2026-06-15T10:00:00", "location": "Houston"},
            {"title": "Bad Event", "start": "not-a-date", "end": "also-bad"},
        ]
        result = get_todays_events(events_raw, target_date=date(2026, 6, 15))
        assert len(result) == 1
        assert result[0]["title"] == "Good Event"

    def test_format_event_time_am(self):
        event = {"title": "Standup", "start": datetime(2026, 6, 15, 9, 0),
                 "end": datetime(2026, 6, 15, 9, 30), "location": "Houston"}
        result = format_event_time(event)
        assert "09:00 AM" in result
        assert "09:30 AM" in result

    def test_format_event_time_pm(self):
        event = {"title": "Review", "start": datetime(2026, 6, 15, 15, 0),
                 "end": datetime(2026, 6, 15, 16, 30), "location": "Houston"}
        result = format_event_time(event)
        assert "03:00 PM" in result
        assert "04:30 PM" in result


# ── 5. Full Report Generation ─────────────────────────────────

class TestReportGeneration:
    def test_report_contains_city_name(self):
        report = build_full_report([], CURRENT_CLEAR, HOURLY_EMPTY)
        assert "HOUSTON" in report or "Houston" in report

    def test_report_no_events_shows_message(self):
        report = build_full_report([], CURRENT_CLEAR, HOURLY_EMPTY)
        assert "No events" in report

    def test_report_shows_current_temperature(self):
        report = build_full_report([], CURRENT_CLEAR, HOURLY_EMPTY)
        assert "80" in report  # CURRENT_CLEAR temp

    def test_report_shows_event_count(self):
        report = build_full_report([EVENT_OUTDOOR, EVENT_INDOOR], CURRENT_CLEAR, HOURLY_EMPTY)
        assert "2 event" in report

    def test_report_contains_personalized_signoff(self):
        report = build_full_report([], CURRENT_CLEAR, HOURLY_EMPTY)
        assert "Shashank" in report

    def test_report_with_rain_contains_umbrella(self):
        report = build_full_report([EVENT_INDOOR], CURRENT_RAIN, HOURLY_EMPTY)
        assert "umbrella" in report.lower() or "rain" in report.lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
