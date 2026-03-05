from intent import parse_intent
import sys
import threading
import subprocess
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtCore import Qt

SAMPLE_RATE = 44100
DURATION = 4
DEVICE = 4

def record_audio():
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16', device=DEVICE)
    sd.wait()
    wav.write("/tmp/anya_input.wav", SAMPLE_RATE, audio)

def transcribe():
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe("/tmp/anya_input.wav", language="hi")
    text = " ".join([s.text for s in segments])
    print(f"Heard: {text}")
    return text

class AnyaLauncher(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(400, 80)
        screen = QApplication.desktop().screenGeometry()
        self.move(screen.width()//2 - 200, screen.height()//2 - 40)
        self.label = QLabel("🎙 Listening...", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setFixedSize(400, 80)
        self.label.setStyleSheet("""
            background-color: #1e1e2e;
            color: #cdd6f4;
            font-size: 24px;
            border-radius: 16px;
        """)

    def start(self):
        t = threading.Thread(target=self.listen_and_close)
        t.start()

    def listen_and_close(self):
        record_audio()
        text = transcribe()
        action, target = parse_intent(text)
        print(f"Action: {action} | Target: {target}")
        if action and target:
            if action == "open":
                subprocess.Popen([target])
            elif action == "close":
                subprocess.run(["pkill", "-f", target])
        QApplication.quit()

app = QApplication(sys.argv)
window = AnyaLauncher()
window.show()
window.start()
sys.exit(app.exec_())