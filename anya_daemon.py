import shlex
from intent import parse_intent, APP_MAP, ALIASES
import sys
import threading
import subprocess
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG, pyqtSignal, QObject, QTimer, pyqtSlot
from PyQt5.QtGui import QPainter, QColor, QLinearGradient, QFont, QPen
import socket
import os
import time
import math

SAMPLE_RATE = 44100
DURATION = 2
DEVICE = 4
SOCKET_PATH = "/tmp/anya.sock"
CLOSE_SOCKET_PATH = "/tmp/anya_close.sock"

print("Anya: Loading model...")
model = WhisperModel("small", device="cpu", compute_type="int8")
print("Anya: Model ready.")
subprocess.Popen([
    "notify-send", 
    "Anya Ready 🎙",
    "Alt+Space se activate karo",
    "--urgency=normal"
])

def record_audio():
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE,
                   channels=1, dtype='int16', device=DEVICE)
    sd.wait()
    wav.write("/tmp/anya_input.wav", SAMPLE_RATE, audio)


def transcribe():
    segments, _ = model.transcribe(
        "/tmp/anya_input.wav", language="en", beam_size=1)
    text = " ".join([s.text for s in segments])
    return text


class AnyaLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setFixedSize(520, 72)
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width()//2 - 260, screen.height()//2 - 36)

        self.text = "🎙  Listening..."
        self.state = "listening"
        self._angle = 0.0
        self._breath = 0.0
        self._breath_dir = 1

        self.timer = QTimer()
        self.timer.timeout.connect(self._animate)
        self.timer.start(16)

    def _animate(self):
        if self.state == "listening":
            self._breath += 0.03 * self._breath_dir
            if self._breath >= 1.0:
                self._breath_dir = -1
            elif self._breath <= 0.0:
                self._breath_dir = 1
        elif self.state in ["opening", "closing", "web"]:
            self._angle = (self._angle + 4) % 360
        self.update()

    def set_state(self, state, text):
        self.state = state
        self.text = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.fillRect(self.rect(), Qt.transparent)

        w, h = self.width(), self.height()
        border = 3
        radius = h // 2

        if self.state == "listening":
            alpha = int(120 + 100 * self._breath)
            colors = [
                QColor(100, 80, 255, alpha),
                QColor(180, 60, 255, alpha),
                QColor(80, 160, 255, alpha),
            ]
        elif self.state == "heard":
            colors = [QColor(0, 200, 255), QColor(0, 255, 200)]
        elif self.state in ["opening", "web"]:
            colors = [QColor(0, 255, 120), QColor(0, 200, 255)]
        elif self.state == "closing":
            colors = [QColor(255, 80, 80), QColor(255, 150, 0)]
        else:
            colors = [QColor(255, 60, 60), QColor(200, 0, 100)]

        angle_rad = math.radians(self._angle)
        cx, cy = w / 2, h / 2
        grad = QLinearGradient(
            cx + math.cos(angle_rad) * w,
            cy + math.sin(angle_rad) * h,
            cx + math.cos(angle_rad + math.pi) * w,
            cy + math.sin(angle_rad + math.pi) * h
        )
        for i, color in enumerate(colors):
            grad.setColorAt(i / max(len(colors) - 1, 1), color)

        painter.setPen(QPen(grad, border * 2))
        painter.drawRoundedRect(
            border, border, w - border*2, h - border*2, radius, radius)

        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(18, 18, 28, 240))
        painter.drawRoundedRect(
            border*2, border*2, w - border*4, h - border*4, radius-2, radius-2)

        painter.setPen(QColor(210, 220, 255))
        font = QFont("monospace", 16)
        font.setWeight(QFont.Medium)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self.text)
        painter.end()

    def start_listening(self):
        t = threading.Thread(target=self.listen_and_close)
        t.start()

    def start_close_listening(self):
        t = threading.Thread(target=self.close_and_done)
        t.start()

    def listen_and_close(self):
        record_audio()
        text = transcribe()

        if not text.strip():
            QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                     Q_ARG(str, "error"), Q_ARG(str, "❓  Try again..."))
            time.sleep(1.2)
            QMetaObject.invokeMethod(self, "hide", Qt.QueuedConnection)
            return

        QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                 Q_ARG(str, "heard"), Q_ARG(str, f'🗣  "{text}"'))
        time.sleep(0.8)

        action, target = parse_intent(text)

        if action == "settings":
            subprocess.Popen(["python", os.path.expanduser("~/anyago/anya_settings.py")])
            QMetaObject.invokeMethod(self, "hide", Qt.QueuedConnection)
        elif action and target:
            if action == "web":
                QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                         Q_ARG(str, "web"), Q_ARG(str, f"🌐  {target}"))
                time.sleep(0.8)
                subprocess.Popen(["firefox", target])
            elif action == "open":
                app_name = target.split("/")[-1]
                QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                         Q_ARG(str, "opening"), Q_ARG(str, f"⚡  Opening {app_name}..."))
                time.sleep(0.8)
                subprocess.Popen([target])
            elif action == "close":
                app_name = target.split("/")[-1]
                QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                         Q_ARG(str, "closing"), Q_ARG(str, f"🛑  Closing {app_name}..."))
                time.sleep(0.8)
                subprocess.run(["pkill", "-f", target])
            elif action == "system":
                QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                             Q_ARG(str, "closing"), Q_ARG(str, f"⚙  {target}..."))
                time.sleep(0.8)
                subprocess.run(shlex.split(target))
                QMetaObject.invokeMethod(self, "hide", Qt.QueuedConnection)
        else:
            QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                     Q_ARG(str, "error"), Q_ARG(str, "❓  Samajh nahi aaya"))
            time.sleep(1.2)
        global is_active
        is_active = False

        QMetaObject.invokeMethod(self, "hide", Qt.QueuedConnection)

    def close_and_done(self):
        record_audio()
        text = transcribe()

        if not text.strip():
            QMetaObject.invokeMethod(self, "hide", Qt.QueuedConnection)
            return

        QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                 Q_ARG(str, "heard"), Q_ARG(str, f'🗣  "{text}"'))
        time.sleep(0.8)

        text_clean = text.lower().strip()
        target = None

        for alias, app_name in ALIASES.items():
            if alias in text_clean:
                target = APP_MAP.get(app_name)
                break

        if not target:
            for app_name in APP_MAP:
                if app_name in text_clean:
                    target = APP_MAP[app_name]
                    break

        if target:
            app_name = target.split("/")[-1]
            QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                     Q_ARG(str, "closing"), Q_ARG(str, f"🛑  Closing {app_name}..."))
            time.sleep(0.8)
            subprocess.run(["pkill", "-f", target])
        else:
            QMetaObject.invokeMethod(self, "_set_state_slot", Qt.QueuedConnection,
                                     Q_ARG(str, "error"), Q_ARG(str, "❓  App nahi mila"))
            time.sleep(1.2)

        QMetaObject.invokeMethod(self, "hide", Qt.QueuedConnection)

    @pyqtSlot(str, str)
    def _set_state_slot(self, state, text):
        self.state = state
        self.text = text
        self.update()


class Communicator(QObject):
    trigger = pyqtSignal()
    close_trigger = pyqtSignal()


comm = Communicator()


is_active = False

def on_trigger():
    global is_active
    if is_active:
        return
    is_active = True
    window.set_state("listening", "🎙  Listening...")
    window.show()
    window.start_listening()


def on_close_trigger():
    window.set_state("closing", "🛑  Close what?")
    window.show()
    window.start_close_listening()


comm.trigger.connect(on_trigger)
comm.close_trigger.connect(on_close_trigger)


def socket_listener():
    if os.path.exists(SOCKET_PATH):
        os.remove(SOCKET_PATH)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(SOCKET_PATH)
    server.listen(1)
    print("Anya: Waiting for trigger...")
    while True:
        conn, _ = server.accept()
        conn.close()
        comm.trigger.emit()


def close_socket_listener():
    if os.path.exists(CLOSE_SOCKET_PATH):
        os.remove(CLOSE_SOCKET_PATH)
    server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    server.bind(CLOSE_SOCKET_PATH)
    server.listen(1)
    print("Anya: Close listener ready...")
    while True:
        conn, _ = server.accept()
        conn.close()
        comm.close_trigger.emit()


app = QApplication(sys.argv)
window = AnyaLauncher()

t = threading.Thread(target=socket_listener, daemon=True)
t.start()

t2 = threading.Thread(target=close_socket_listener, daemon=True)
t2.start()

sys.exit(app.exec_())