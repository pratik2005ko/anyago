import subprocess
import sounddevice as sd
import scipy.io.wavfile as wav
from faster_whisper import WhisperModel
import threading

SAMPLE_RATE = 44100
DURATION = 4
DEVICE = 4

def record_audio():
    print("Listening...")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16', device=DEVICE)
    sd.wait()
    wav.write("/tmp/anya_input.wav", SAMPLE_RATE, audio)
    print("Recorded.")

def transcribe():
    model = WhisperModel("tiny", device="cpu", compute_type="int8")
    segments, _ = model.transcribe("/tmp/anya_input.wav", language="hi")
    text = " ".join([s.text for s in segments])
    print(f"Heard: {text}")
    return text

def launch_rofi():
    result = subprocess.run(["pgrep", "-f", "rofi"], capture_output=True)
    if result.returncode == 0:
        subprocess.run(["pkill", "-f", "rofi"])
    else:
        t = threading.Thread(target=record_audio)
        t.start()
        subprocess.run(["rofi", "-show", "drun"])
        t.join()
        transcribe()

launch_rofi()