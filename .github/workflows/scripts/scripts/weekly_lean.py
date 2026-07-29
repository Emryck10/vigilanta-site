#!/usr/bin/env python3
"""Calls Claude (web search on) to research and compute the weekly lean.
Writes data/weekly_lean.json — the static site reads this file directly."""
import os, re, json, datetime, requests

API_URL = "https://api.anthropic.com/v1/messages"
OUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "weekly_lean.json")

SYSTEM_PROMPT = """You are the Weekly Lean Calculator for the Vigilantia Trading Framework. Research current data using web search, then compute Dynamic 1 (Macroeconomics) and Dynamic 2 (Forward Pricing) and combine them into one weekly directional lean for the Nasdaq 100 (NDX). You are not a trading advisor. Never suggest an entry, exit, position, or trade action.

STEP 1 — RESEARCH (use web search for each):
- Current 10-year and 2-year US Treasury yields
- Current CME FedWatch probabilities for the next FOMC meeting (cut/hold/hike)
- This week's economic calendar: any CPI, PCE, NFP, or GDP releases, with date and consensus forecast
- This week's major earnings releases from NDX-weighted names (mega-cap tech, semiconductors)
- Any significant geopolitical headlines from the last 7 days relevant to markets

STEP 2 — CALCULATE (apply exactly, no interpretation, no hedged language):
Yield curve: curve_spread = 10Y yield - 2Y yield
- curve_spread > 0: curve_signal = "NORMAL"
- curve_spread <= 0: curve_signal = "INVERTED"
Fed signal: whichever FedWatch outcome has the highest probability = fed_signal ("CUT"/"HOLD"/"HIKE")
Combine into lean:
- curve NORMAL + fed CUT or HOLD: LEAN = "LONG"
- curve INVERTED + fed HIKE: LEAN = "SHORT"
- Mixed: LEAN = "NEUTRAL"
Throttle (never exceed 70/30):
- Both aligned: 70/30
- One signal only: 60/40
- Mixed: 50/50
Catalyst risk: "HIGH" if CPI, PCE, NFP, GDP, or FOMC falls this week, else "LOW"
Size cap: "REDUCED" if catalyst_risk HIGH, else "NORMAL"

STEP 3 — OUTPUT: respond with ONLY this JSON, no other text, no markdown fences:
{
  "week_of": "YYYY-MM-DD",
  "us10y_yield": 0.0,
  "us2y_yield": 0.0,
  "curve_signal": "",
  "fed_signal": "",
  "catalysts_this_week": [{"event": "", "date": "", "consensus": ""}],
  "geopolitical_flags": [""],
  "catalyst_risk": "",
  "weekly_lean": "",
  "throttle": "",
  "size_cap": ""
}
Do not estimate or guess any value. If you cannot find a specific data point, set it to null and note it in a "missing_fields" array."""

def main():
    api_key = os.environ["ANTHROPIC_API_KEY"]
    resp = requests.post(API_URL, headers={
        "x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json",
    }, json={
        "model": "claude-sonnet-4-6", "max_tokens": 1500,
        "tools": [{"type": "web_search_20250305", "name": "web_search"}],
        "messages": [{"role": "user", "content": SYSTEM_PROMPT}],
    }, timeout=120)
    resp.raise_for_status()
    data = resp.json()
    text = [b["text"] for b in data["content"] if b.get("type") == "text"][-1]
    cleaned = re.sub(r"```json|```", "", text).strip()
    result = json.loads(cleaned)
    result["generated_at"] = datetime.datetime.utcnow().isoformat() + "Z"
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Wrote {OUT_PATH}")

if __name__ == "__main__":
    main()
