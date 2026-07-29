#!/usr/bin/env python3
"""Daily 7 AM ET overnight review. Reads the stored weekly lean, researches
overnight developments, flags whether it still holds. Writes data/overnight_review.json"""
import os, re, json, datetime, requests

API_URL = "https://api.anthropic.com/v1/messages"
BASE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")
LEAN_PATH = os.path.join(BASE_DIR, "weekly_lean.json")
OUT_PATH = os.path.join(BASE_DIR, "overnight_review.json")

def build_prompt(stored_lean, catalysts):
    return f"""You are the Overnight Review for the Vigilantia Trading Framework. Research what happened overnight using web search, and check it against the stored weekly lean below. Never recalculate or restate the lean. Never suggest a trade action.

Stored weekly lean: {stored_lean}
Scheduled catalysts this week: {json.dumps(catalysts)}

STEP 1 — RESEARCH: market-moving headlines (Fed/macro/geopolitical) from the last 12 hours; current NDX/Nasdaq futures % change overnight; current VIX level and change from prior close; whether any scheduled catalyst released overnight and its result vs consensus.

STEP 2 — CLASSIFY: "LEAN INTACT" if nothing overnight materially challenges the stored lean, or "REVIEW NEEDED" if a scheduled catalyst surprised or overnight action is materially inconsistent with the lean.

STEP 3 — OUTPUT ONLY this JSON, no other text:
{{
  "headlines_summary": "",
  "ndx_futures_pct_change": 0.0,
  "vix_change": 0.0,
  "catalysts_released_overnight": [{{"event": "", "result": "", "vs_consensus": ""}}],
  "status": "",
  "stored_lean_reference": "{stored_lean}"
}}"""

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
        "model": "claude-sonnet-4-6", "max_tokens": 1200,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": build_prompt(stored_lean, catalysts)}],
    }, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    text = [b["text"] for b in data["content"] if b.get("type") == "text"][-1]
    cleaned = re.sub(r"```json|```", "", text).strip()
    result = json.loads(cleaned)
    result["checked_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
