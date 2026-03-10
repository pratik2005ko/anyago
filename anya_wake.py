import pvporcupine
import sounddevice as sd
import socket
import time

PICOVOICE_KEY = "ikKhOCwfT1U0vLfiTN0MCmlGkdzzWVbXtvtO81zGf5vs+hjUQNPryg=="
SOCKET_PATH = "/tmp/anya.sock"
WAKE_WORD_PATH = "/home/pratik/anyago/wake/Hey-Anya_en_linux_v4_0_0.ppn"


def send_trigger():
    try:
        time.sleep(0.8)
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        client.connect(SOCKET_PATH)
        client.sendall(b"TRIGGER")
        client.close()
        print("✅ Hey Anya detected — TRIGGER sent")
        time.sleep(3)  # 3 second tak dobara trigger mat bhejo
    except Exception as e:
        print(f"❌ Socket error: {e}")

def main():
    porcupine = pvporcupine.create(
        access_key=PICOVOICE_KEY,
        keyword_paths=[WAKE_WORD_PATH],
    )

    print(f"🎙 Anya Wake — listening on device 4 (PipeWire)")
    print("Say 'Hey Anya' to activate...")

    with sd.InputStream(
        samplerate=porcupine.sample_rate,
        channels=1,
        dtype='int16',
        device=4,
        blocksize=porcupine.frame_length,
    ) as stream:
        while True:
            pcm, _ = stream.read(porcupine.frame_length)
            pcm = pcm.flatten()
            result = porcupine.process(pcm)
            if result >= 0:
                send_trigger()

    porcupine.delete()


if __name__ == "__main__":
    main()