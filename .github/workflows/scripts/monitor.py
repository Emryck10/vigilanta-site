#!/usr/bin/env python3
"""30-min flag-only monitor. Reads stored lean, checks last 30 min of news.
Writes data/monitor.json (overwrites each run with latest check + a rolling flag log)."""
import os, re, json, datetime, requests

API_URL = "https://api.anthropic.com/v1/messages"
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
LEAN_PATH = os.path.join(BASE_DIR, "weekly_lean.json")
OUT_PATH = os.path.join(BASE_DIR, "monitor.json")

def build_prompt(stored_lean, catalysts):
    return f"""You are the News Monitor for the Vigilantia Trading Framework. Research the last 30 minutes of news using web search and check whether anything material has happened. Never recalculate the lean. Never suggest a trade action.

Stored weekly lean: {stored_lean}
Scheduled catalysts this week: {json.dumps(catalysts)}

STEP 1 — RESEARCH: market-moving news in the last 30 minutes (Fed/macro/geopolitical/major NDX-weighted earnings only).
STEP 2 — CLASSIFY: MATERIAL (a scheduled catalyst just released, or a genuine shock) vs NOISE (routine/rehashed).
STEP 3 — OUTPUT ONLY this JSON, no other text:
{{"material_found": false, "flag_summary": "", "stored_lean_reference": "{stored_lean}"}}"""

def main():
    api_key = os.environ["ANTHROPIC_API_KEY"]
    stored_lean, catalysts = "UNKNOWN", []
    if os.path.exists(LEAN_PATH):
        with open(LEAN_PATH) as f:
            lean_data = json.load(f)
            stored_lean = lean_data.get("weekly_lean", "UNKNOWN")
            catalysts = lean_data.get("catalysts_this_week", [])

    resp = requests.post(API_URL, headers={
        "x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json",
    }, json={
        "model": "claude-sonnet-4-6", "max_tokens": 800,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": build_prompt(stored_lean, catalysts)}],
    }, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    text = [b["text"] for b in data["content"] if b.get("type") == "text"][-1]
    cleaned = re.sub(r"```json|```", "", text).strip()
    result = json.loads(cleaned)
    result["checked_at"] = datetime.datetime.utcnow().isoformat() + "Z"

    history = []
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH) as f:
            try:
                prev = json.load(f)
                history = prev.get("history", [])
            except Exception:
                history = []
    history.append(result)
    history = history[-20:]

    with open(OUT_PATH, "w") as f:
        json.dump({"latest": result, "history": history}, f, indent=2)
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
