import whisper
import sounddevice as sd
import numpy as np
import tkinter as tk
import asyncio
from pythonosc import udp_client
import wave
import time
import os

# Set the IP and port for VRChat's OSC server (localhost and port 9000)
ip = "127.0.0.1"
port = 9000

# Create an OSC client to send messages
client = udp_client.SimpleUDPClient(ip, port)

# Load the Whisper model (you can choose between 'tiny', 'base', 'small', 'medium', 'large')
model = whisper.load_model("base")

def show_overlay(message):
    # Create the root window
    root = tk.Tk()
    root.overrideredirect(True)  # Remove window borders (overlay-like behavior)
    root.attributes('-topmost', True)  # Keep the window on top

    # Set the size of the window and place it in the center of the screen
    window_width = 500
    window_height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_right = int(screen_width / 2 - window_width / 2)
    position_down = int(screen_height - window_height - 50)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")

    # Make the background transparent
    root.config(bg='black')
    root.wm_attributes('-alpha', 0.7)

    # Create a label for the message
    message_label = tk.Label(root, text=message, font=("Helvetica", 16), fg="white", bg="black", wraplength=350)
    message_label.pack(expand=True)

    # Close the overlay after 2.5 seconds
    root.after(2500, root.destroy)

    # Run the overlay window
    root.mainloop()

async def async_show_overlay(message):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, show_overlay, message)

async def async_send_message(address, args):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, client.send_message, address, args)

# Function to send recognized text to VRChat chatbox
async def chatbox(text):
    print(f"Sending text to chatbox: {text}")
    await async_show_overlay(f"Sending text to chatbox: {text}")
    # Send the recognized text to the chatbox
    await async_send_message("/chatbox/input", [text, True])

def record_audio(duration=5, sample_rate=16000):
    """Record audio from the microphone for a given duration."""
    print("Recording audio...")
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()  # Wait until the recording is finished
    return np.squeeze(audio)

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
        audio_data = record_audio(duration=5)

        # Save the recorded audio to a temporary file in the correct format for Whisper
        temp_audio_filename = os.path.abspath("temp_audio.wav")
        save_audio_to_wav(audio_data, temp_audio_filename)

        # Use Whisper to transcribe the recorded audio
        print("Transcribing audio using Whisper...")
        result = model.transcribe(temp_audio_filename)
        recognized_text = result["text"].strip()

        if recognized_text:
            print(f"Recognized text: {recognized_text}")
            # Send recognized text to VRChat chatbox
            await chatbox(recognized_text)
        else:
            print("No speech detected, try again.")
            await async_show_overlay("No speech detected, try again.")
    except Exception as e:
        print(f"Error recognizing speech: {e}")
        await async_show_overlay(f"Error recognizing speech: {e}")

# Main asynchronous loop to continuously listen and recognize speech
async def main():
    while True:
        await recognize_and_send()
        time.sleep(1)  # Optional: Add a short delay between recognitions if needed

# Run the async main loop
if __name__ == "__main__":
    asyncio.run(main())
