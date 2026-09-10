#!/usr/bin/env python3
"""Update the Recent Activity section of the profile README with relative timestamps."""
import json
import urllib.request
from datetime import datetime, timezone

USERNAME = "andregil003"
README_PATH = "README.md"
MAX_LINES = 5

START_MARKER = "<!--RECENT_ACTIVITY:start-->"
END_MARKER = "<!--RECENT_ACTIVITY:end-->"


def fetch_events():
    url = f"https://api.github.com/users/{USERNAME}/events/public?per_page=30"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "profile-readme-updater",
            "Accept": "application/vnd.github+json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def time_ago(iso_str):
    dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    seconds = int((now - dt).total_seconds())
    if seconds < 60:
        return "justo ahora"
    minutes = seconds // 60
    if minutes < 60:
        return f"hace {minutes} min"
    hours = minutes // 60
    if hours < 24:
        return f"hace {hours} h"
    days = hours // 24
    if days < 30:
        return f"hace {days} d"
    months = days // 30
    return f"hace {months} meses"


def main():
    events = fetch_events()
    lines = []
    for ev in events:
        if ev["type"] == "PushEvent":
            repo = ev["repo"]["name"]
            url = f"https://github.com/{repo}"
            when = time_ago(ev["created_at"])
            lines.append(f"{len(lines) + 1}. ⬆️ Pushed to [{repo}]({url}) · {when}<br>")
            if len(lines) >= MAX_LINES:
                break

    if not lines:
        lines = ["_No recent activity._"]

    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    start_idx = content.index(START_MARKER) + len(START_MARKER)
    end_idx = content.index(END_MARKER)
    new_block = "\n" + "\n".join(lines) + "\n"
    content = content[:start_idx] + new_block + content[end_idx:]

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"Updated {len(lines)} activity lines")


if __name__ == "__main__":
    main()