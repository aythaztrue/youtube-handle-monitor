import json
import os
import urllib.error
import urllib.request
from pathlib import Path

HANDLE = "a2u"
PAGE_URL = f"https://www.youtube.com/@%7BHANDLE%7D"
STATE_FILE = Path("monitor_state.txt")
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]


def discord(message):
    payload = json.dumps({"content": message}).encode()
    request = urllib.request.Request(
        WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        if response.status not in (200, 204):
            raise RuntimeError("Discord notification failed")


def check_page():
    request = urllib.request.Request(
        PAGE_URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode("utf-8", errors="replace")
            code = response.status
    except urllib.error.HTTPError as error:
        if error.code == 404:
            return "POSSIBLE_OPENING"
        raise RuntimeError(
            f"YouTube returned HTTP {error.code}; status unknown"
        )

    lower = html.lower()

    if "this page isn't available" in lower:
        return "POSSIBLE_OPENING"

    if "channelid" in lower or '"externalid"' in lower:
        return "CHANNEL_FOUND"

    return "UNKNOWN"


previous = (
    STATE_FILE.read_text().strip()
    if STATE_FILE.exists()
    else ""
)

current = check_page()
print(f"Handle @{HANDLE}: {current}")

if current != "UNKNOWN" and current != previous:
    if current == "POSSIBLE_OPENING":
        message = (
            f"🔎 @{HANDLE} may be available!\n"
            "This is NOT confirmation. Check immediately:\n"
            "https://studio.youtube.com/"
        )
    else:
        message = (
            f"📺 @{HANDLE} appears to resolve to a channel:\n"
            f"{PAGE_URL}"
        )

    discord(message)

STATE_FILE.write_text(current + "\n")
elif current == "UNKNOWN":
    print("Page response was inconclusive; keeping previous state.")
