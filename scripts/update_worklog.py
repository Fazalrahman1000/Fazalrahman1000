"""
Queries the GitHub Search API for commits authored by GITHUB_USERNAME on the
current UTC date, then prepends a summary entry to WORKLOG.md.

Required environment variables (set as repo secrets, wired up in the workflow):
  WORKLOG_TOKEN     - a GitHub Personal Access Token with 'repo' scope
                       (needed so private repo commits are included; a token
                       with only public_repo scope also works if you only
                       want public activity tracked)
  GITHUB_USERNAME   - your GitHub username, e.g. "Fazalrahman1000"
"""

import os
import sys
from datetime import datetime, timezone

import requests

TOKEN = os.environ["WORKLOG_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]
WORKLOG_PATH = "WORKLOG.md"

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}


def get_today_commits():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    query = f"author:{USERNAME} author-date:{today}"
    url = "https://api.github.com/search/commits"
    resp = requests.get(url, headers=HEADERS, params={"q": query, "per_page": 100})
    resp.raise_for_status()
    return today, resp.json().get("items", [])


def build_entry(date_str, commits):
    if not commits:
        return f"### {date_str}\n\n_No commits recorded._\n"

    repos = {}
    for c in commits:
        repo_name = c["repository"]["full_name"]
        repos.setdefault(repo_name, 0)
        repos[repo_name] += 1

    lines = [f"### {date_str}", "", f"**Total commits:** {len(commits)}", ""]
    for repo, count in sorted(repos.items(), key=lambda x: -x[1]):
        lines.append(f"- `{repo}` — {count} commit{'s' if count != 1 else ''}")
    lines.append("")
    return "\n".join(lines)


def update_worklog(entry):
    with open(WORKLOG_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    marker = "<!-- LOG_START -->"
    if marker not in content:
        print("LOG_START marker not found in WORKLOG.md", file=sys.stderr)
        sys.exit(1)

    idx = content.index(marker) + len(marker)
    new_content = content[:idx] + "\n\n" + entry + content[idx:]

    with open(WORKLOG_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)


if __name__ == "__main__":
    date_str, commits = get_today_commits()
    entry = build_entry(date_str, commits)
    update_worklog(entry)
    print(f"Worklog updated for {date_str} ({len(commits)} commits).")
