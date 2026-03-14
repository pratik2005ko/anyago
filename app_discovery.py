import os
import glob
import json

CACHE_PATH = os.path.expanduser("~/.cache/anya/apps.json")

DESKTOP_DIRS = [
    "/usr/share/applications/",
    os.path.expanduser("~/.local/share/applications/"),
    "/var/lib/flatpak/exports/share/applications/",
    os.path.expanduser("~/.local/share/flatpak/exports/share/applications/"),
]
APPIMAGE_DIR = os.path.expanduser("~/Applications/")

def parse_desktop_file(filepath):
    name = None
    exec_cmd = None
    try:
        with open(filepath, 'r', errors='ignore') as f:
            for line in f:
                if line.startswith("Name=") and name is None:
                    name = line.strip().split("=", 1)[1].lower()
                if line.startswith("Exec=") and exec_cmd is None:
                    raw = line.strip().split("=", 1)[1]
                    parts = raw.split()
                    # flatpak: "/usr/bin/flatpak run --branch=stable ... com.App.Id @@ %U @@"
                    if parts and parts[0].endswith("flatpak"):
                        # flags (--)  aur placeholders (%, @@) strip karo
                        clean = [p for p in parts if not p.startswith(("-", "%", "@@"))]
                        # clean[-1] = app-id (e.g. com.spotify.Client)
                        exec_cmd = "flatpak run " + clean[-1]
                    else:
                        exec_cmd = parts[0]  # normal binary
    except:
        pass
    return name, exec_cmd

def _cache_valid():
    if not os.path.exists(CACHE_PATH):
        return False
    cache_mtime = os.path.getmtime(CACHE_PATH)
    for directory in DESKTOP_DIRS:
        if os.path.exists(directory):
            if os.path.getmtime(directory) > cache_mtime:
                return False
    return True

def discover_apps():
    if _cache_valid():
        with open(CACHE_PATH, 'r') as f:
            return json.load(f)

    app_map = {}

    for directory in DESKTOP_DIRS:
        for filepath in glob.glob(directory + "*.desktop"):
            name, exec_cmd = parse_desktop_file(filepath)
            if name and exec_cmd:
                app_map[name] = exec_cmd

    if os.path.exists(APPIMAGE_DIR):
        for filepath in glob.glob(APPIMAGE_DIR + "*.AppImage"):
            name = os.path.basename(filepath).split(".AppImage")[0].lower()
            app_map[name] = filepath

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, 'w') as f:
        json.dump(app_map, f)

    return app_map

if __name__ == "__main__":
    apps = discover_apps()
    for name, cmd in sorted(apps.items()):
        print(f"{name} → {cmd}")