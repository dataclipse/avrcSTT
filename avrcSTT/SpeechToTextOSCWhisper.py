import whisper, sounddevice as sd, numpy as np, tkinter as tk, asyncio, wave, os, warnings, signal, noisereduce as nr
from pythonosc import udp_client
from threading import Thread
from scipy.signal import butter, lfilter


# Suppress future and user warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)

# Set the IP and port for VRChat's OSC server (localhost and port 9000)
ip = "127.0.0.1"
port = 9000

# Create an OSC client to send messages
client = udp_client.SimpleUDPClient(ip, port)

# Load the Whisper model (you can choose between 'tiny', 'base', 'small', 'medium', 'large')
model = whisper.load_model("small")

# Init variables to be used in the overlay creation
overlay_root = None
message_label = None

def run_asyncio_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# Function to stop the asyncio loop
def stop_asyncio_loop(loop):
    loop.call_soon_threadsafe(loop.stop)

# Function to handle Ctrl+C (KeyboardInterrupt)
def handle_exit(signal, frame):
    print("Ctrl+C detected. Stopping the asyncio loop and terminating the program...")
    stop_asyncio_loop(asyncio_loop)  # Stop the asyncio loop
    print("Joining Thread...")
    asyncio_thread.join()  # Wait for the thread to finish
    print("Calling System Exit...")
    os._exit(0)  # Terminate the program

# Set up the signal handler for Ctrl+C (SIGINT)
signal.signal(signal.SIGINT, handle_exit)

# Start an asynico event loop in a separate thread
asyncio_loop = asyncio.new_event_loop()
asyncio_thread = Thread(target=run_asyncio_loop, args=(asyncio_loop,))
asyncio_thread.start()

def show_overlay(message):
    global overlay_root, message_label
    
    if overlay_root is None:
        # Create the root window
        overlay_root = tk.Tk()
        overlay_root.overrideredirect(True)  # Remove window borders (overlay-like behavior)
        overlay_root.attributes('-topmost', True)  # Keep the window on top

        # Set the size of the window and place it in the center of the screen
        window_width = 500
        window_height = 100
        screen_width = overlay_root.winfo_screenwidth()
        screen_height = overlay_root.winfo_screenheight()
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height - window_height - 50)
        overlay_root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

        # Make the background transparent
        overlay_root.config(bg='black')
        overlay_root.wm_attributes('-alpha', 0.7)

        # Create a label for the message
        message_label = tk.Label(overlay_root, text=message, font=("Helvetica", 16), fg="white", bg="black", wraplength=350)
        message_label.pack(expand=True)

        # Run the overlay window
        overlay_root.mainloop()
    else:
        message_label.config(text=message)

async def async_show_overlay(message):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, show_overlay, message)

async def async_send_message(address, args):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, client.send_message, address, args)

# Function to send recognized text to VRChat chatbox
async def chatbox(text):
    print(f"Sending text to chatbox: {text}")
    # Send the recognized text to the chatbox
    await async_send_message("/chatbox/input", [text, True])
    asyncio.run_coroutine_threadsafe(async_show_overlay(f"Sending text to chatbox: {text}"), asyncio_loop)

# Function to record the audio from microphone
def record_audio(duration=5, sample_rate=16000):
    """Record audio from the microphone for a given duration."""
    print("Recording audio...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Wait until the recording is finished

    return np.squeeze(audio)

async def save_audio_to_wav_sync(audio_data, filename):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, save_audio_to_wav, audio_data, filename, 16000)

# Function to save the audio data recorded to a temporary wav file
def save_audio_to_wav(audio_data, filename, sample_rate=16000):
    """Save numpy audio data to a WAV file."""
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono audio
        wf.setsampwidth(2)  # 16-bit audio
        wf.setframerate(sample_rate)
        wf.writeframes((audio_data * 32767).astype(np.int16).tobytes())

# Function to recognize speech from the microphone and send it to the chatbox
async def recognize_and_send():
    try:
        # Record audio from the microphone
        asyncio.run_coroutine_threadsafe(async_show_overlay("Recording audio..."), asyncio_loop)
        audio_data = record_audio(duration=5)

        # Save the recorded audio to a temporary file in the correct format for Whisper
        temp_audio_filename = os.path.abspath("temp_audio.wav")  # Use an absolute path
        await save_audio_to_wav_sync(audio_data, temp_audio_filename)

        # Ensure the file exists after saving
        if not os.path.exists(temp_audio_filename):
            raise FileNotFoundError(f"File {temp_audio_filename} not found after saving.")

        # Use Whisper to transcribe the recorded audio
        print("Transcribing audio using Whisper...")
        asyncio.run_coroutine_threadsafe(async_show_overlay("Transcribing audio using Whisper..."), asyncio_loop)
        result = model.transcribe(temp_audio_filename)
        recognized_text = result["text"].strip()

        if recognized_text:
            print(f"Recognized text: {recognized_text}")
            # Send recognized text to VRChat chatbox
            await chatbox(recognized_text)
            asyncio.run_coroutine_threadsafe(async_show_overlay(recognized_text), asyncio_loop)
        else:
            print("No speech detected, try again.")
            asyncio.run_coroutine_threadsafe(async_show_overlay("No speech detected, try again."), asyncio_loop)

    except FileNotFoundError as e:
        print(f"File error: {e}")
        asyncio.run_coroutine_threadsafe(async_show_overlay(f"File error: {e}"), asyncio_loop)
    except Exception as e:
        print(f"Error recognizing speech: {e}")
        asyncio.run_coroutine_threadsafe(async_show_overlay(f"Error recognizing speech: {e}"), asyncio_loop)

# Start the main asynchronous loop to continuously listen and recognize speech
async def main():
    try:
        while True:
            print("Running... Press CTRL+C to stop.")
            await recognize_and_send()
    except KeyboardInterrupt:
        print("Program Terminated by user.")

# Run the async main loop
if __name__ == "__main__":
    asyncio.run(main())
