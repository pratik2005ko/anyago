# 🎙 ANyA — Voice + Hotkey Powered App Launcher for Arch Linux

ANyA is a lightweight voice-controlled app launcher for Arch Linux. Press `Super+Z`, say what you want — ANyA opens apps, closes them, searches the web, or runs system commands. No mouse needed.

> Say "open Firefox" → Firefox opens. Say "bye" → system shuts down. That's it.

---

## ✨ Features

- 🎙 **Wake word activation** — Say "Hey Anya" to activate hands-free
- ⌨️ **Hotkey trigger** — `Super+Z` to activate instantly
- 🌐 **Web search** — "search something" opens in Firefox
- ⚙️ **System commands** — power off, reboot, lock, bluetooth
- 🪄 **Animated pill UI** — Minimal floating capsule with gradient animations
- 📋 **Alias support** — Custom app nicknames via `aliases.json`
- 🗂️ **App discovery** — Auto-detects installed apps including Flatpak
- 📝 **Logging** — All actions logged to `~/.local/share/anya/logs.txt`

---

## 🛠️ Requirements

- Arch Linux (or Arch-based distro)
- Hyprland compositor
- Python 3.10+
- A working microphone

### Python dependencies

```bash
pip install faster-whisper sounddevice scipy PyQt5 pvporcupine
```

---

## 🔑 Picovoice Setup (Wake Word)

ANyA uses [Picovoice Porcupine](https://picovoice.ai/) for wake word detection ("Hey Anya").

1. Sign up at [picovoice.ai](https://picovoice.ai/) and generate a free **Access Key**
2. Download the **Hey-Anya** wake word model file (`.ppn`) for Linux from the Picovoice console
3. Place the `.ppn` file inside the `wake/` folder in the project directory
4. Open `anya_wake.py` and set your key and path:

```python
PICOVOICE_KEY = "your-access-key-here"
WAKE_WORD_PATH = "/home/youruser/anyago/wake/Hey-Anya_en_linux_v4_0_0.ppn"
```

---

## 🎤 Microphone Setup

ANyA's audio device is currently **hardcoded** due to system-specific mic behavior.

To find your correct device index, run:

```bash
python3 -c "import sounddevice as sd; print(sd.query_devices())"
```

Look for your input device in the list and note its index number. Then open `anya_daemon.py` and update:

```python
def get_audio_device():
    return 4  # ← replace 4 with your device index
```

### Sample Rate

Default sample rate is `16000 Hz`. If your mic uses a different rate, update this line in `anya_daemon.py`:

```python
SAMPLE_RATE = 16000  # change if your mic differs
```

---

## 🧠 Whisper Model Configuration

ANyA uses `faster-whisper` for transcription. The default config is optimized for low VRAM (integrated GPU / CPU-only):

```python
model = WhisperModel("small", device="cpu", compute_type="int8")
```

**If you have a dedicated GPU** with enough VRAM, you can use a larger model for better accuracy:

```python
# medium or large — requires 4GB+ VRAM
model = WhisperModel("medium", device="cuda", compute_type="float16")
```

---

## ⚙️ System Commands

Built-in system commands (stack dependent):

| Say this | Command |
|----------|---------|
| "bye" | `systemctl poweroff` |
| "reboot" | `systemctl reboot` |
| "lock" | `swaylock -c 1e1e2eff` |
| "disconnect" | `bluetoothctl power off` |
| "connect" | `bluetoothctl power on` |

> ⚠️ These depend on your stack. `swaylock` requires Wayland/Hyprland. Modify `intent.py` to match your setup.

---

## 🏗️ Hyprland Configuration

Add the following to your Hyprland config (`~/.config/hypr/hyprland.conf`):

```bash
# ANyA window rules — clean pill UI, no shadow/border
windowrule = no_shadow on, match:class python3
windowrule = border_size 0, match:class python3

# Hotkey trigger
bind = SUPER, Z, exec, python /home/youruser/anyago/anya_trigger.py

# Auto-start on login
exec-once = python /home/youruser/anyago/anya_daemon.py
exec-once = python /home/youruser/anyago/anya_wake.py
```

> Replace `/home/youruser/anyago/` with your actual project path.

---

## 🗂️ Project Structure

| File | Description |
|------|-------------|
| `anya_daemon.py` | Main daemon — UI, voice recording, transcription, actions |
| `anya_trigger.py` | Sends hotkey trigger to daemon via Unix socket |
| `anya_wake.py` | Wake word listener — "Hey Anya" via Picovoice |
| `anya_close.py` | Sends close-app trigger to daemon |
| `anya_settings.py` | Settings UI |
| `intent.py` | Parses voice commands into actions |
| `app_discovery.py` | Auto-discovers installed apps on the system |
| `aliases.json` | Custom app name aliases (e.g. "browser" → "firefox") |

> `watcher.py` is a V1 prototype — not used in the current version.

---

## 💬 Usage

Once daemon is running, press `Super+Z` or say "Hey Anya":

| Say this | What happens |
|----------|-------------|
| "open Firefox" | Opens Firefox |
| "close Spotify" | Closes Spotify |
| "search neovim plugins" | Opens browser with search |
| "bye" | Powers off system |
| "lock" | Locks screen |

---

## 🚧 V1.1 Coming Soon

- Seamless one-breath commands ("Hey Anya play playlist name")
- Modular daemon — UI, sound, and system as separate drivers
- Volume and brightness control
- Music integration
- Theme framework + avatar system (AnyaNeko)
- Custom URL hotwords

---

## 📜 License

Do whatever you want with it. 🤙

---

Made with 🤍 by [pratik2005ko](https://github.com/pratik2005ko)
