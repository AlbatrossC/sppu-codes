import requests
from .config import DISCORD_WEBHOOK_URL

def send_discord_notification(notification_type, data):
    """Sends a formatted embed message to Discord."""
    if not DISCORD_WEBHOOK_URL:
        print("Discord Webhook URL not set.")
        return

    embed = _build_discord_embed(notification_type, data)
    if not embed:
        return

    payload = {"embeds": [embed]}
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "SPPU-Codes-Bot/1.0 (Vercel; +https://yourwebsite.com)"
    }

    try:
        response = requests.post(
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


def _build_discord_embed(notification_type, data):
    """Builds the appropriate Discord embed based on notification type."""
    if notification_type == "submit":
        return {
            "title": "New Code Submission",
            "color": 5763719,
            "fields": [
                {"name": "Contributor Name", "value": data.get("name", "Anonymous"), "inline": True},
                {"name": "Subject", "value": data.get("subject"), "inline": True},
                {"name": "Branch/Year", "value": f"{data.get('branch')} - {data.get('year')}", "inline": False}
            ],
            "footer": {"text": "Check database for full code"}
        }
    
    elif notification_type == "contact":
        message = data.get("message", "")
        message_snippet = (message[:200] + '...') if len(message) > 200 else message
        return {
            "title": "New Contact Query",
            "color": 15158332,
            "fields": [
                {"name": "From", "value": data.get("name"), "inline": True},
                {"name": "Email", "value": data.get("email"), "inline": True},
                {"name": "Message Snippet", "value": message_snippet, "inline": False}
            ]
        }
    
    elif notification_type == "download":
        user_agent = data.get("user_agent", "")
        ua_snippet = (user_agent[:200] + '...') if len(user_agent) > 200 else user_agent
        return {
            "title": "ZIP Download",
            "color": 3447003,
            "fields": [
                {"name": "Subject", "value": data.get("subject_name", data.get("subject_link", "Unknown")), "inline": True},
                {"name": "Subject Link", "value": data.get("subject_link", "unknown"), "inline": True},
                {"name": "Exam Type", "value": data.get("exam_type", "all"), "inline": True},
                {"name": "Files In ZIP", "value": str(data.get("file_count", 0)), "inline": True},
                {"name": "Success", "value": "Yes" if data.get("success", True) else "No", "inline": True},
                {"name": "From IP", "value": data.get("ip", "unknown"), "inline": False},
                {"name": "User Agent (truncated)", "value": ua_snippet, "inline": False}
            ],
            "footer": {"text": "No file or repo URLs included"}
        }
    
    return None
