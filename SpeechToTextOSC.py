import speech_recognition as sr
from pythonosc import udp_client
import tkinter as tk
import asyncio

# Set the IP and port for VRChat's OSC server (localhost and port 9000)
ip = "127.0.0.1"
port = 9000

# Create an OSC client to send messages
client = udp_client.SimpleUDPClient(ip, port)

# Initialize recognizer
recognizer = sr.Recognizer()

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
    position_right = int(screen_width/2 - window_width/2)
    position_down = int(screen_height - window_height - 50)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
    
    # Make the background transparent
    root.config(bg='black')
    root.wm_attributes('-alpha', 0.7)

    # Create a label for the message
    message_label = tk.Label(root, text=message, font=("Helvetica", 16), fg="white", bg="black", wraplength=350)
    message_label.pack(expand=True)

    # Close the overlay after 5 seconds
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
    # Send the recognized text to the chatbox
    await async_send_message("/chatbox/input", [text, True])
    await async_show_overlay(f"Sending text to chatbox: {text}")

# Function to recognize speech from the microphone and send it to the chatbox
async def recognize_and_send():
    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for noise
        print("Listening for speech...")

        try:
            # Listen for audio from the microphone
            audio = recognizer.listen(source)
            
            # Recognize speech using Google's speech recognition engine
            rt = recognizer.recognize_google(audio)
            print(f"Recognized text: {rt}")
            
            # Send recognized text to VRChat chatbox
            await chatbox(rt)
        except sr.UnknownValueError:
            print("Could not understand audio, try again")
            await async_show_overlay("Could not understand audio, try again")         
        except sr.RequestError as e:
            print(f"Error with the speech recognition service: {e}")

# Main asynchronous loop to continuously listen and recognize speech
async def main():
    while True:
        await recognize_and_send()

# Run the async main loop
if __name__ == "__main__":
    asyncio.run(main())
