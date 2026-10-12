
import json
import os
import urllib.request
import urllib.error
from pathlib import Path

# Settings
HANDLE = "a2u"
URL = f"https://www.youtube.com/@{HANDLE}"

WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]
USER_ID = os.environ["DISCORD_USER_ID"]

STATE_FILE = Path("monitor_state.txt")



def notify(message):
    payload = json.dumps({
        "content": f"<@{USER_ID}> {message}",
        "allowed_mentions": {
            "users": [USER_ID]
        }
    }).encode("utf-8")

    request = urllib.request.Request(
        WEBHOOK,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "YouTubeHandleMonitor/1.0"
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            print(f"Discord notification sent: HTTP {response.status}")

    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="replace")
        print(f"Discord HTTP error: {error.code}")
        print(f"Discord response: {details}")
        raise



def check_handle():
    """Check YouTube's public page; results may be inconclusive."""
    request = urllib.request.Request(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            html = response.read().decode(
                "utf-8", errors="replace"
            ).lower()

        if "this page isn't available" in html:
            return "POSSIBLE_OPENING"

        if '"externalid"' in html or "channelid" in html:
            return "CHANNEL_FOUND"

        return "UNKNOWN"

    except urllib.error.HTTPError as error:
        if error.code == 404:
            return "POSSIBLE_OPENING"

        print(f"YouTube returned HTTP {error.code}; status is unknown.")
        return "UNKNOWN"

    except Exception as error:
        print(f"Could not check YouTube: {error}")
        return "UNKNOWN"


def main():
    previous = (
        STATE_FILE.read_text().strip()
        if STATE_FILE.exists()
        else ""
    )

    current = check_handle()
    print(f"Handle @{HANDLE}: {current}")

    if current == "UNKNOWN":
        print("Inconclusive result; no alert sent.")
        return

    if current == previous:
        print("No change since the previous saved result.")
        return

    if current == "POSSIBLE_OPENING":
        notify(
            f"🔎 @{HANDLE} may be available!\n"
            "This is NOT confirmation. Check YouTube Studio:\n"
            "https://studio.youtube.com/"
        )
    else:
        print(f"@{HANDLE} appears to resolve to a channel.")

    STATE_FILE.write_text(current + "\n")


if __name__ == "__main__":
    notify("✅ Test ping! Your YouTube handle monitor can reach Discord.")
    main()
