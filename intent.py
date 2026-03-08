from rapidfuzz import process, fuzz
from app_discovery import discover_apps
import json
import os
import re

OPEN_KEYWORDS = ["open", "start", "launch"]
CLOSE_KEYWORDS = ["close", "kill", "stop", "band", "bandh"]
WEB_KEYWORD = "visit"
SEARCH_KEYWORD = "search"

APP_MAP = discover_apps()

ALIASES_PATH = os.path.expanduser("~/anyago/aliases.json")

SYSTEM_COMMANDS = {
    "bye": "systemctl poweroff",
    "blind": "swaylock -c 1e1e2eff",
    "disconnect": "bluetoothctl power off",
    "connect": "bluetoothctl power on",
    "reboot": "systemctl reboot",
}

def load_aliases():
    try:
        with open(ALIASES_PATH, 'r') as f:
            return json.load(f)
    except:
        return {}

ALIASES = load_aliases()

def parse_intent(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)

    words = text.split()

    if not words:
        return None, None

    if any(word in text for word in ["fix", "fixed", "fux", "setup", "set up"]):
        return "settings", None

    for cmd, action_cmd in SYSTEM_COMMANDS.items():
        if re.search(rf'\b{cmd}\b', text):
            return "system", action_cmd

    if words[0] == WEB_KEYWORD and len(words) > 1:
        site = words[1]
        url = f"https://www.{site}.com"
        return "web", url

    if words[0] == SEARCH_KEYWORD and len(words) > 1:
        query = "+".join(words[1:])
        url = f"https://www.google.com/search?q={query}"
        return "web", url

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

    for alias, app_name in ALIASES.items():
        if alias in text:
            target = APP_MAP.get(app_name)
            break

    if not target:
        match, score, _ = process.extractOne(text, APP_MAP.keys(), scorer=fuzz.WRatio)
        if score > 85:
            target = APP_MAP[match]

    if target and not action:
        action = "open"

    return action, target