name: Weekly Lean
on:
  schedule:
    # Sunday 12:00 PM ET = 17:00 UTC during EST. During EDT (summer), ET is
    # UTC-4, so this actually fires ~1:00 PM ET in summer. Adjust the hour
    # below (+/-1) if you want it exact year-round.
    - cron: '0 17 * * 0'
  workflow_dispatch: {}  # lets you trigger it manually from the Actions tab too

permissions:
  contents: write

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install requests
      - run: python scripts/weekly_lean.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Commit updated data
        run: |
          git config user.name "vigilantia-bot"
          git config user.email "actions@github.com"
          git add data/weekly_lean.json
          git diff --staged --quiet || git commit -m "Update weekly lean"
          git push
