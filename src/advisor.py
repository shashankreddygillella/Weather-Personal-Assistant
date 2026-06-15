"""
advisor.py
Rule-based advice engine. Takes weather conditions and events,
returns actionable, context-aware advice for each event.
"""

# ── Thresholds ────────────────────────────────────────────────
RAIN_CODE_MIN = 51          # WMO codes >= 51 = some form of precipitation
STORM_CODE_MIN = 95         # WMO codes >= 95 = thunderstorm
HIGH_TEMP_F = 95            # °F — heat advisory threshold
LOW_TEMP_F = 45             # °F — cold advisory threshold
HIGH_WIND_MPH = 25          # mph — wind advisory threshold
HIGH_PRECIP_PROB = 50       # % — umbrella threshold


def is_raining(weathercode: int) -> bool:
    return weathercode >= RAIN_CODE_MIN


def is_stormy(weathercode: int) -> bool:
    return weathercode >= STORM_CODE_MIN


def is_hot(temperature: float) -> bool:
    return temperature is not None and temperature >= HIGH_TEMP_F


def is_cold(temperature: float) -> bool:
    return temperature is not None and temperature <= LOW_TEMP_F


def is_windy(windspeed: float) -> bool:
    return windspeed is not None and windspeed >= HIGH_WIND_MPH


def is_outdoor_event(event: dict) -> bool:
    """Heuristic: events with outdoor-ish keywords are flagged."""
    outdoor_keywords = ["site", "visit", "outdoor", "park", "field", "gym", "run", "walk"]
    title_lower = event["title"].lower()
    return any(kw in title_lower for kw in outdoor_keywords)


def generate_advice(event: dict, current: dict, hourly: list) -> list:
    """
    Generate a list of advice strings for a single event
    based on current weather and hourly forecast near event time.
    """
    advice = []
    title = event["title"]
    event_hour = event["start"].strftime("%Y-%m-%dT%H:00")

    # Find the closest hourly forecast to event start time
    hourly_match = next(
        (h for h in hourly if h["time"] == event_hour),
        None
    )

    # Use hourly if available, else fall back to current
    code = hourly_match["weathercode"] if hourly_match else current["weathercode"]
    temp = hourly_match["temperature"] if hourly_match else current["temperature"]
    precip_prob = hourly_match["precipitation_probability"] if hourly_match else None
    wind = current["windspeed"]

    # ── Rain / Storm Rules ─────────────────────────────────────
    if is_stormy(code):
        advice.append(f"⛈️  STORM WARNING during '{title}' — consider rescheduling or moving indoors.")
    elif is_raining(code):
        advice.append(f"🌧️  Rain expected during '{title}' — bring an umbrella.")
    elif precip_prob is not None and precip_prob >= HIGH_PRECIP_PROB:
        advice.append(f"☂️  {precip_prob}% chance of rain during '{title}' — safe to bring an umbrella.")

    # ── Temperature Rules ──────────────────────────────────────
    if is_hot(temp):
        advice.append(f"🌡️  It will be {temp}°F during '{title}' — stay hydrated and wear light clothing.")
    elif is_cold(temp):
        advice.append(f"🧥  It will be {temp}°F during '{title}' — wear a jacket.")

    # ── Wind Rules ─────────────────────────────────────────────
    if is_windy(wind):
        advice.append(f"💨  Wind speeds at {wind} mph — secure loose items if outdoors for '{title}'.")

    # ── Outdoor Event Rules ────────────────────────────────────
    if is_outdoor_event(event) and is_raining(code):
        advice.append(f"🏗️  '{title}' appears to be an outdoor event — rain gear strongly recommended.")

    # ── All Clear ─────────────────────────────────────────────
    if not advice:
        advice.append(f"✅  Weather looks fine for '{title}' — no special precautions needed.")

    return advice


def build_full_report(events: list, current: dict, hourly: list) -> str:
    """Build the complete text report for all today's events."""
    lines = []
    lines.append("=" * 55)
    lines.append("   🌤  WEATHER-AWARE PERSONAL ASSISTANT — HOUSTON, TX")
    lines.append("=" * 55)
    lines.append(f"\n📍 Current Conditions: {current['description']}")
    lines.append(f"   🌡  Temperature : {current['temperature']}°F")
    lines.append(f"   💧 Precipitation: {current['precipitation']} in")
    lines.append(f"   💨 Wind Speed   : {current['windspeed']} mph\n")

    if not events:
        lines.append("📅  No events found for today in your calendar.\n")
    else:
        lines.append(f"📅  You have {len(events)} event(s) today:\n")
        for event in events:
            from src.schedule import format_event_time
            lines.append(f"  🕐 {format_event_time(event)}  |  {event['title']}")
            advice_list = generate_advice(event, current, hourly)
            for tip in advice_list:
                lines.append(f"      {tip}")
            lines.append("")

    lines.append("=" * 55)
    lines.append("   Stay prepared. Have a great day, Shashank! 🚀")
    lines.append("=" * 55)
    return "\n".join(lines)
