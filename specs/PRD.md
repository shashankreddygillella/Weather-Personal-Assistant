# Product Requirements Document (PRD)
## Weather-Aware Personal Assistant — Houston, TX

**Author:** Shashank Reddy Gillella  
**Course:** Gen AI and Applications  
**Version:** 1.0  
**Date:** June 2026

---

## 1. Purpose & Vision

This CLI application acts as a personal daily briefing assistant. Every morning, it fetches live weather conditions for Houston, TX, reads the user's schedule from a local JSON file, and synthesizes actionable, weather-aware advice for each event of the day.

The goal is not just to display weather — it is to *reason* about how weather intersects with the user's plans and surface specific, useful guidance.

---

## 2. Problem Statement

Users check weather apps and calendars separately. There is no single tool that says: *"You have an outdoor site visit at 11am and it will be storming — you should reschedule or bring rain gear."* This assistant bridges that gap with zero friction: one command, one report.

---

## 3. Target User

A working professional in Houston, TX with a daily schedule that includes a mix of indoor and outdoor events, who wants a single morning CLI briefing instead of juggling multiple apps.

---

## 4. Core Features

| Feature | Description | Priority |
|---|---|---|
| Weather Fetch | Pull live data from Open-Meteo API (no API key required) | Must Have |
| Schedule Read | Parse `calendar.json` for today's events | Must Have |
| Rule-Based Advice | Generate per-event advice based on weather thresholds | Must Have |
| Hourly Matching | Match event start time to hourly forecast for precision | Should Have |
| Outdoor Detection | Heuristic keyword detection for outdoor events | Should Have |
| CLI Output | Clean, emoji-enhanced terminal report | Must Have |
| Graceful Errors | Clear error messages if API or file is unavailable | Must Have |

---

## 5. Advice Rules (Rule Engine Logic)

The advisor in `advisor.py` applies the following rules in order for each event:

| Condition | Threshold | Advice Generated |
|---|---|---|
| Thunderstorm | WMO code ≥ 95 | Warn to reschedule or move indoors |
| Rain | WMO code ≥ 51 | Suggest umbrella |
| High precip probability | ≥ 50% | Suggest umbrella as precaution |
| High temperature | ≥ 95°F | Hydration + light clothing reminder |
| Low temperature | ≤ 45°F | Jacket reminder |
| High wind | ≥ 25 mph | Secure loose items warning |
| Outdoor event + rain | Both conditions true | Extra rain gear warning |
| No conditions triggered | — | All-clear confirmation (✅) |

---

## 6. System Architecture

```
weather-assistant/
├── main.py              ← Orchestrator (CLI entry point, zero business logic)
├── calendar.json        ← User's schedule (editable JSON)
├── src/
│   ├── weather.py       ← API layer: fetch + parse Open-Meteo weather data
│   ├── schedule.py      ← Data layer: read + filter today's events
│   └── advisor.py       ← Logic layer: rules engine + report builder
├── tests/
│   └── test_logic.py    ← 22 automated tests for core logic
├── specs/
│   └── PRD.md           ← This document (source of truth)
└── docs/
    └── rules.md         ← Persona and constraints
```

**Separation of concerns is strict:**
- `weather.py` only knows about weather data
- `schedule.py` only knows about calendar data
- `advisor.py` only knows about rules and combining the two
- `main.py` only orchestrates — it never contains business logic

---

## 7. Data Sources

- **Weather API:** [Open-Meteo](https://open-meteo.com/) — free, no API key, HTTPS, updated hourly
- **Schedule:** Local `calendar.json` file — user-maintained, ISO 8601 datetime format

---

## 8. Non-Functional Requirements

- Must run with Python 3.8+ and zero third-party dependencies (stdlib only — `urllib`, `json`, `datetime`, `os`, `sys`)
- `requests` is used if available but falls back to `urllib.request` gracefully
- All API calls must have a 10-second timeout
- Graceful error messages (not raw tracebacks) if API or file is unavailable
- Tests must be runnable with `pytest` without any additional setup
- No file exceeds 150 lines

---

## 9. Out of Scope (v1.0)

- LLM-powered advice (rule-based only for v1)
- GUI or web interface
- Multi-city support
- Push notifications or scheduling
- Google Calendar / Outlook integration

---

## 10. Success Criteria

- App runs end-to-end with `python main.py`
- All 22 automated tests pass with `pytest tests/ -v`
- At least one weather condition triggers a specific advisory per run
- Code is modular: no file exceeds 150 lines
- Zero business logic in `main.py`
