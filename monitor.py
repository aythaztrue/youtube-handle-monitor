
import json
import os
import urllib.request
import urllib.error

HANDLE = "a2u"
URL = f"https://www.youtube.com/@{HANDLE}"
WEBHOOK = os.environ["DISCORD_WEBHOOK_URL"]


def notify(message):
    payload = json.dumps({"content": message}).encode("utf-8")
    request = urllib.request.Request(
        WEBHOOK,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        print(f"Discord notification sent: HTTP {response.status}")


request = urllib.request.Request(
    URL,
    headers={"User-Agent": "Mozilla/5.0"},
)

try:
    with urllib.request.urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace").lower()

    if "channelid" in html or '"externalid"' in html:
        print(f"@{HANDLE} appears to belong to a channel.")
    else:
        print(f"Could not confirm whether @{HANDLE} is available.")
        print("No alert sent because the result is inconclusive.")

except urllib.error.HTTPError as error:
    if error.code == 404:
        notify(
            f"🔎 YouTube returned a 404 for @{HANDLE}. "
            "This does NOT confirm availability. Check manually: "
            "https://www.youtube.com/@a2u"
        )
    else:
        raise RuntimeError(
            f"YouTube returned HTTP {error.code}; status is unknown."
        )
