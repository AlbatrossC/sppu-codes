import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from .config import DISCORD_WEBHOOK_URL

_http = requests.Session()
_executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="discord-notify")


def _safe_text(value, fallback, limit):
    text = (value or fallback or "").strip()
    if not text:
        text = fallback
    if len(text) > limit:
        return text[:limit - 3] + "..."
    return text


def _safe_field(name, value, inline=True, limit=1024):
    return {
        "name": name,
        "value": _safe_text(value, "Not provided", limit),
        "inline": inline
    }


def send_discord_notification(notification_type, data):
    """Sends a formatted embed message to Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not set.")
        return

    embed = _build_discord_embed(notification_type, data)
    if not embed:
        return

    payload = {
        "username": "SPPU Codes",
        "embeds": [embed]
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SPPU-Codes-Bot/1.0 (Vercel; +https://sppucodes.in)"
    }

    try:
        response = _http.post(
            DISCORD_WEBHOOK_URL,
            json=payload,
            headers=headers,
            timeout=5
        )
        response.raise_for_status()
        print(f"Discord notification sent successfully. Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Failed to send Discord notification: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Discord Response: {e.response.text}")


def send_discord_notification_async(notification_type, data):
    _executor.submit(send_discord_notification, notification_type, data)
    return True


def _build_discord_embed(notification_type, data):
    """Builds the appropriate Discord embed based on notification type."""
    timestamp = datetime.now(timezone.utc).isoformat()

    if notification_type == "submit":
        return {
            "title": "New Code Submission",
            "color": 5763719,
            "timestamp": timestamp,
            "description": "A new answer submission was received from the website.",
            "fields": [
                _safe_field("Contributor", data.get("name"), True),
                _safe_field("Subject", data.get("subject"), True),
                _safe_field("Email", data.get("email"), False),
                _safe_field("Question", data.get("question"), False, 300),
                _safe_field("Code Length", str(data.get("code_length", 0)), True),
                _safe_field("IP", data.get("ip_address"), True),
                _safe_field("Source", data.get("source_url"), False),
                _safe_field("User-Agent", data.get("user_agent"), False)
            ],
            "footer": {"text": "Check the database for the full submission"}
        }

    if notification_type == "contact":
        return {
            "title": "New Contact Query",
            "color": 15158332,
            "timestamp": timestamp,
            "description": "A new contact form message was received.",
            "fields": [
                _safe_field("From", data.get("name"), True),
                _safe_field("Email", data.get("email"), True),
                _safe_field("Message", data.get("message"), False, 500),
                _safe_field("IP", data.get("ip_address"), True),
                _safe_field("Source", data.get("source_url"), False),
                _safe_field("User-Agent", data.get("user_agent"), False)
            ]
        }

    return None
