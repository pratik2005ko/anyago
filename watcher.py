from intent import parse_intent
import sys
import threading
import subprocess
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG
import time

SAMPLE_RATE = 44100
DURATION = 4
DEVICE = 4

model = WhisperModel("tiny", device="cpu", compute_type="int8")

def record_audio():
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16', device=DEVICE)
    sd.wait()
    wav.write("/tmp/anya_input.wav", SAMPLE_RATE, audio)

def transcribe():
    segments, _ = model.transcribe("/tmp/anya_input.wav", language="hi", beam_size=1)
    text = " ".join([s.text for s in segments])
    return text

class AnyaLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 80)
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width()//2 - 250, screen.height()//2 - 40)

        self.label = QLabel("🎙 Listening...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(500, 80)
        self.label.setStyleSheet("""
            background-color: #1e1e2e;
            color: #cdd6f4;
            font-size: 22px;
            border-radius: 16px;
        """)

    def set_text(self, text):
        QMetaObject.invokeMethod(self.label, "setText", Qt.QueuedConnection, Q_ARG(str, text))

    def start(self):
        t = threading.Thread(target=self.listen_and_close)
        t.start()

    def listen_and_close(self):
        record_audio()
        text = transcribe()

        self.set_text(f'🗣 "{text}"')
        time.sleep(0.8)

        action, target = parse_intent(text)

        if action and target:
            app_name = target.split("/")[-1]
            if action == "open":
                self.set_text(f"⚡ Opening {app_name}...")
            elif action == "close":
                self.set_text(f"🛑 Closing {app_name}...")
            time.sleep(0.8)

            if action == "open":
                subprocess.Popen([target])
            elif action == "close":
                subprocess.run(["pkill", "-f", target])
        else:
            self.set_text("❓ Samajh nahi aaya")
            time.sleep(1.2)

        QApplication.quit()

app = QApplication(sys.argv)
window = AnyaLauncher()
window.show()
window.start()
sys.exit(app.exec_())