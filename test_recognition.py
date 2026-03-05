from faster_whisper import WhisperModel
import sounddevice as sd
import scipy.io.wavfile as wav
from intent import parse_intent

SAMPLE_RATE = 44100
DURATION = 4
DEVICE = 4

model = WhisperModel("small", device="cpu", compute_type="int8")

def record_and_test():
    print("Bol ab...")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='int16', device=DEVICE)
    sd.wait()
    wav.write("/tmp/anya_input.wav", SAMPLE_RATE, audio)
    
    segments, _ = model.transcribe("/tmp/anya_input.wav", language="en", beam_size=1)
    text = " ".join([s.text for s in segments])
    
    print(f"Whisper ne suna : '{text}'")
    
    action, target = parse_intent(text)
    print(f"Action          : {action}")
    print(f"Target          : {target}")
    print("-" * 40)

for i in range(5):
    input(f"Test {i+1}/5 — Enter dabaao phir bolo: ")
    record_and_test()