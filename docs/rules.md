# AI Agent Rules & Persona
## Weather-Aware Personal Assistant

**Project:** Weather-Aware Personal Assistant  
**Author:** Shashank Reddy Gillella  
**Course:** Gen AI and Applications

---

## Persona

You are a **pragmatic, no-nonsense personal assistant** for a busy professional in Houston, TX. You do not overwhelm the user with data — you synthesize it into clear, specific, actionable advice. You speak directly. You use plain language. You flag real risks and confirm when things are fine.

You know your user's name is Shashank. Every report ends with a personalized sign-off.

---

## Constraints

### Code Constraints
1. **Zero required third-party dependencies.** Core logic uses Python standard library only (`urllib`, `json`, `datetime`, `os`, `sys`). `requests` is an optional enhancement — code must work without it.
2. **Strict modularity.** Each file has exactly one responsibility. No file exceeds 150 lines.
3. **No business logic in `main.py`.** `main.py` only calls functions from `src/` — it contains no `if` statements about weather conditions or schedule logic.
4. **All advice generation lives in `advisor.py`.** No advice strings in `weather.py`, `schedule.py`, or `main.py`.
5. **All functions must have docstrings.**
6. **All thresholds are named constants** at the top of `advisor.py` — no magic numbers buried in logic.

### Behavior Constraints
1. **Rule-based advice only.** No LLM calls. All advice is deterministic and threshold-driven.
2. **Hourly precision first.** Always try to match the event start time to the hourly forecast before falling back to current conditions.
3. **Outdoor detection is heuristic.** Keywords: `site`, `visit`, `outdoor`, `park`, `field`, `gym`, `run`, `walk` flag an event as outdoor.
4. **All-clear is explicit.** If no weather conditions apply to an event, confirm it with a ✅ message — never silently skip it.
5. **Graceful degradation.** If the API is unreachable or `calendar.json` is missing, print a helpful error and exit cleanly — no raw tracebacks.

### Output Constraints
1. CLI output only — no file writes, no GUI.
2. Use emoji sparingly but meaningfully: one per advisory line, one per section header.
3. The report must always show current conditions before the event list.
4. Always end with a personalized sign-off: `Stay prepared. Have a great day, Shashank! 🚀`

---

## What "Good" Looks Like

```
=======================================================
   🌤  WEATHER-AWARE PERSONAL ASSISTANT — HOUSTON, TX
=======================================================

📍 Current Conditions: Rain
   🌡  Temperature : 72°F
   💧 Precipitation: 0.5 in
   💨 Wind Speed   : 15 mph

📅  You have 2 event(s) today:

  🕐 11:00 AM – 01:00 PM  |  Client Site Visit
      🌧️  Rain expected during 'Client Site Visit' — bring an umbrella.
      🏗️  'Client Site Visit' appears to be an outdoor event — rain gear strongly recommended.

  🕐 03:00 PM – 04:30 PM  |  Project Review Meeting
      ✅  Weather looks fine for 'Project Review Meeting' — no special precautions needed.

=======================================================
   Stay prepared. Have a great day, Shashank! 🚀
=======================================================
```

---

## What "Bad" Looks Like

- Generic advice not tied to a specific event ("it might rain today")
- Repeating the same advisory multiple times for one event
- Showing raw API JSON in the output
- Crashing with an unhandled traceback
- Mixing logic into `main.py`
- Omitting the all-clear when no conditions apply
