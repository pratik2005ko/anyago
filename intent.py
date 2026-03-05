from app_discovery import discover_apps

OPEN_KEYWORDS = ["kholo", "khol", "open", "start", "chalo", "chalao"]
CLOSE_KEYWORDS = ["band", "bandh", "close", "kill", "stop", "bnd"]

APP_MAP = discover_apps()

def parse_intent(text):
    text = text.lower().strip()

    action = None
    target = None

    for word in OPEN_KEYWORDS:
        if word in text:
            action = "open"
            break

    for word in CLOSE_KEYWORDS:
        if word in text:
            action = "close"
            break

    for app_name in APP_MAP:
        if app_name in text:
            target = APP_MAP[app_name]
            break

    return action, target