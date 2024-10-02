import speech_recognition as sr
from pythonosc import udp_client
import asyncio
import websockets
import json

# Set the IP and port for VRChat's OSC server (localhost and port 9000)
ip = "127.0.0.1"
port = 9000

# Create an OSC client to send messages
client = udp_client.SimpleUDPClient(ip, port)

# Initialize recognizer
recognizer = sr.Recognizer()

# Function to send recognized text to XSOverlay
async def xsoMessage(text):
    uri = "ws://127.0.0.1:42070"  # XSOverlay WebSocket API address
    message = {
    "type": 1,
    "content": text,
    "timeout": 5.0,
    "opacity": 1.0,
    }
    # Convert the message to JSON format
    message_json = json.dumps(message)
    
    # Establish WebSocket connection to XSOverlay
    async with websockets.connect(uri) as websocket:
        await websocket.send(message_json)
        print(f"Sent message: {message_json}")

# Function to send recognized text to VRChat chatbox
def chatbox(text):
    print(f"Sending text to chatbox: {text}")
    asyncio.get_event_loop().run_until_complete(xsoMessage(f"Sending text to chatbox: {text}"))
    # Send the recognized text to the chatbox
    client.send_message("/chatbox/input", [text, True])

# Function to recognize speech from the microphone and send it to the chatbox
def recognize_and_send():
    with sr.Microphone() as source:
        print("Adjusting for ambient noise, please wait...")
        #xsoMessage("Adjusting for ambient noise, please wait...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for noise
        print("Listening for speech...")
        #xsoMessage("Listening for speech...")  

        try:
            # Listen for audio from the microphone
            audio = recognizer.listen(source)
            
            # Recognize speech using Google's speech recognition engine
            rt = recognizer.recognize_google(audio)
            print(f"Recognized text: {rt}")
            
            # Send recognized text to VRChat chatbox
            chatbox(rt)
        except sr.UnknownValueError:
            print("Could not understand audio try again")
            asyncio.get_event_loop().run_until_complete(xsoMessage("Could not understand audio try again"))
            #xsoMessage("Could not understand audio try again")             
        except sr.RequestError as e:
            print(f"Error with the speech recognition service; {e}")

# Continuously listen and recognize speech from the microphone
while True:
    recognize_and_send()