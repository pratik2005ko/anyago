import os
import glob

DESKTOP_DIRS = [
    "/usr/share/applications/",
    os.path.expanduser("~/.local/share/applications/"),
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
                    exec_cmd = line.strip().split("=", 1)[1]
                    exec_cmd = exec_cmd.split()[0]  # sirf pehla word — binary
    except:
        pass
    return name, exec_cmd

def discover_apps():
    app_map = {}

    # Pacman + Flatpak
    for directory in DESKTOP_DIRS:
        for filepath in glob.glob(directory + "*.desktop"):
            name, exec_cmd = parse_desktop_file(filepath)
            if name and exec_cmd:
                app_map[name] = exec_cmd

    # AppImages
    if os.path.exists(APPIMAGE_DIR):
        for filepath in glob.glob(APPIMAGE_DIR + "*.AppImage"):
            name = os.path.basename(filepath).split(".AppImage")[0].lower()
            app_map[name] = filepath

    return app_map

if __name__ == "__main__":
    apps = discover_apps()
    for name, cmd in sorted(apps.items()):
        print(f"{name} → {cmd}")