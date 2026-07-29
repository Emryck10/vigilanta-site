name: Overnight Review
on:
  schedule:
    # 7:00 AM ET = 12:00 UTC during EST. Adjust +/-1 hour for EDT if needed.
    - cron: '0 12 * * 1-5'
  workflow_dispatch: {}

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
      - run: python scripts/overnight_review.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
      - name: Commit updated data
        run: |
          git config user.name "vigilantia-bot"
          git config user.email "actions@github.com"
          git add data/overnight_review.json
          git diff --staged --quiet || git commit -m "Update overnight review"
          git push
