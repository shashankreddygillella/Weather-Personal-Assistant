# 🌤 Weather-Aware Personal Assistant — Houston, TX

A CLI personal assistant that fetches **live weather** for Houston, TX, reads your daily schedule, and delivers **event-specific, weather-aware advice** every morning — one command, one report.

**Author:** Shashank Reddy Gillella | Gen AI and Applications | June 2026

---

## Quick Start

```bash
# No installation needed — uses Python standard library only
python main.py
```

**Requirements:** Python 3.8+  
_(Optional: `pip install requests` for slightly faster HTTP — the app works without it)_

---

##  Run Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

Expected output: **46 passed**

---

## Project Structure

```
weather-assistant/
├── main.py              ← CLI entry point (orchestrator only — zero business logic)
├── calendar.json        ← Your daily schedule (edit this!)
├── src/
│   ├── weather.py       ← Fetches & parses Open-Meteo API data
│   ├── schedule.py      ← Reads & filters calendar.json for today's events
│   └── advisor.py       ← Rule-based advice engine + report builder
├── tests/
│   └── test_logic.py    ← 46 automated tests across 5 test classes
├── specs/
│   └── PRD.md           ← Product Requirements Document (source of truth)
└── docs/
    └── rules.md         ← AI agent persona & constraints
```

---

## Customizing Your Schedule

Edit `calendar.json` to add your own events:

```json
{
  "events": [
    {
      "title": "Client Site Visit",
      "start": "2026-06-15T11:00:00",
      "end": "2026-06-15T13:00:00",
      "location": "Houston, TX"
    }
  ]
}
```

**Tip:** Events with keywords like `site`, `visit`, `gym`, `outdoor`, `run`, `walk`, `park`, or `field` are automatically flagged as outdoor events and get extra weather warnings.

---

## How the Advice Engine Works

The rule engine in `advisor.py` checks each event in order:

| # | Condition | Threshold | Advice |
|---|---|---|---|
| 1 | Thunderstorm | WMO code ≥ 95 | ⛈️ Reschedule / move indoors |
| 2 | Rain | WMO code ≥ 51 | 🌧️ Bring umbrella |
| 3 | High precip probability | ≥ 50% | ☂️ Precautionary umbrella |
| 4 | Heat | ≥ 95°F | 🌡️ Hydration + light clothing |
| 5 | Cold | ≤ 45°F | 🧥 Wear a jacket |
| 6 | Wind | ≥ 25 mph | 💨 Secure loose items |
| 7 | Outdoor event + rain | Both true | 🏗️ Rain gear strongly recommended |
| 8 | No conditions | — | ✅ All clear |

The engine uses **hourly forecast data** matched to each event's start hour for precision, falling back to current conditions if no match is found.

---

## Data Source

Weather data from [Open-Meteo](https://open-meteo.com/) — free, no API key required, updated hourly.

---

## Vibe Report

### 1. Where did the AI's "vibe" drift?

The AI agent drifted in two consistent ways:

**Drift #1 — Architectural laziness.** The AI's default instinct was to write everything in `main.py` as one long procedural script. Left unchecked, it would fetch weather, filter events, and print advice all in a single function. It kept "forgetting" the modular constraint unless explicitly told to enforce it on every generation step.

**Drift #2 — Incomplete domain knowledge.** The AI's WMO weather code mapping was incomplete — it handled the most common codes (0, 63, 95) but silently omitted the 80–82 range (rain showers), which are among the most frequent conditions during Houston summers. It confidently generated a mapping that looked complete but wasn't. This is a classic AI confidence-without-correctness failure.

---

### 2. When did I use the "Builder Hammer"?

**Manual fix #1 — Hourly time-matching logic.**  
The AI generated a `generate_advice()` function that always fell back to current conditions instead of matching the event start time to the hourly slot. The time string it generated for matching was in the wrong format (`%Y-%m-%dT%H:%M` instead of `%Y-%m-%dT%H:00`), so the `next()` lookup always returned `None`. I manually rewrote the time-matching block:

```python
# AI's broken version:
event_hour = event["start"].strftime("%Y-%m-%dT%H:%M")

# My fix:
event_hour = event["start"].strftime("%Y-%m-%dT%H:00")
```

A single character difference, but it broke the most important feature of the entire app.

**Manual fix #2 — WMO code completeness.**  
I manually audited and completed the `WMO_CODES` dictionary in `weather.py`, adding codes 80 (`Light showers`), 81 (`Showers`), and 82 (`Heavy showers`) that the AI omitted. Without these, showers in Houston would silently display as `Unknown` in the output.

---

### 3. Most Successful Steering Prompt

> *"You are a software architect, not a developer. Your job is to enforce separation of concerns. The file `advisor.py` must be the ONLY file that contains if-statements about weather conditions. `main.py` must contain zero business logic — only function calls. Rewrite the structure with this constraint as non-negotiable."*

This single prompt restructured the entire codebase into the clean modular architecture it has now. Three things made it effective:

1. **A role, not a task** — "you are an architect" changed how the AI reasoned about the problem
2. **A negative constraint** — "zero business logic in main.py" is easier for the AI to verify than a positive instruction like "be modular"
3. **The word non-negotiable** — this prevented the AI from finding clever workarounds that technically satisfied the rule while violating its intent

---

