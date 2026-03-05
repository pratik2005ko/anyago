from app_discovery import discover_apps
import json
import os

OPEN_KEYWORDS = ["kholo", "khol", "open", "start", "chalo", "chalao"]
CLOSE_KEYWORDS = ["band", "bandh", "close", "kill", "stop", "bnd"]

APP_MAP = discover_apps()

ALIASES_PATH = os.path.expanduser("~/anyago/aliases.json")

def load_aliases():
    try:
        with open(ALIASES_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

ALIASES = load_aliases()

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

    # pehle alias check karo
    for alias, app_name in ALIASES.items():
        if alias in text:
            target = APP_MAP.get(app_name)
            break

    # agar alias se nahi mila toh direct APP_MAP mein dhundho
    if not target:
        for app_name in APP_MAP:
            if app_name in text:
                target = APP_MAP[app_name]
                break

    return action, target