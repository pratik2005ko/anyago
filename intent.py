from app_discovery import discover_apps
import json
import os
import re
import subprocess

OPEN_KEYWORDS = ["open", "start", "launch"]
CLOSE_KEYWORDS = ["close", "kill", "stop", "band", "bandh"]
WEB_KEYWORD = "visit"
SEARCH_KEYWORD = "search"

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
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text)

    words = text.split()

    # web prefix
    if words[0] == WEB_KEYWORD and len(words) > 1:
        site = words[1]
        url = f"https://www.{site}.com"
        return "web", url

    # search prefix
    if words[0] == SEARCH_KEYWORD and len(words) > 1:
        query = "+".join(words[1:])
        url = f"https://www.google.com/search?q={query}"
        return "web", url

    # open/close
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

    # alias check
    for alias, app_name in ALIASES.items():
        if alias in text:
            target = APP_MAP.get(app_name)
            break

    # direct APP_MAP
    if not target:
        for app_name in APP_MAP:
            if app_name in text:
                target = APP_MAP[app_name]
                break

    return action, target