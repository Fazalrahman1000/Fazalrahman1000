name: Daily Work Log

on:
  schedule:
    # Runs every day at 23:00 UTC. Adjust the cron to fit your timezone.
    - cron: "0 23 * * *"
  workflow_dispatch: {}  # allows manually triggering a run from the Actions tab

permissions:
  contents: write

jobs:
  update-worklog:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: pip install requests

      - name: Update WORKLOG.md
        env:
          WORKLOG_TOKEN: ${{ secrets.WORKLOG_TOKEN }}
          GITHUB_USERNAME: ${{ github.repository_owner }}
        run: python scripts/update_worklog.py

      - name: Commit and push changes
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add WORKLOG.md
          git diff --cached --quiet || git commit -m "docs: update daily work log"
          git push
