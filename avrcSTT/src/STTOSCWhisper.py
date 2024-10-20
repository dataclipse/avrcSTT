import whisper, speech_recognition as sr, numpy as np, warnings, torch, threading, os, webrtcvad, scipy.ndimage
from sys import platform
from pythonosc import udp_client
from queue import Queue, Empty
from datetime import datetime, timedelta, timezone
from time import sleep

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class STTOSCWhisper:
    def __init__(self, whisper_model='small', sample_rate=16000, frame_duration=20, log_callback=None):
        # Set the IP and port for VRChat's OSC server (localhost and port 9000)
        self.ip = "127.0.0.1"
        self.port = 9000

        # Create an OSC client to send messages
        self.client = udp_client.SimpleUDPClient(self.ip, self.port)
        self.phrase_time = None
        self.data_queue = Queue()

        # Using Google Speech Recognizer for stream audio recording
        self.recorder = sr.Recognizer()
        self.recorder.energy_threshold = 3
        self.recorder.dynamic_energy_threshold = False
        self.source = sr.Microphone(sample_rate=16000)

        # Initialize WebRTC VAD to detect voice on audio chunks
        self.vad = webrtcvad.Vad(2)
        self.sample_rate = sample_rate
        self.frame_duration = frame_duration
        self.frame_size = int (sample_rate * frame_duration / 1000)

        # Load the Whisper model
        self.model = whisper.load_model(whisper_model)
        
        # Audio Chunk size
        self.record_timeout = 5
        
        # Time between speaking before a new message is sent to VRC
        self.phrase_timeout = 5
        self.transcription = ['']
        self.log_callback = log_callback

        self._running = False
        self.stop_event = threading.Event()

    def log(self, message):
        # Init the log directory and log file path
        log_dir = "logs"
        log_file = os.path.join(log_dir, f"{datetime.now().strftime('%Y-%m-%d')}.log")

        # Ensure the log directory exists
        os.makedirs(log_dir, exist_ok=True)
        
        # Create a log entry with a timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"

        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

        # Write the message to the log file
        try:
            with open(log_file, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Failed to write to log file: {e}")

    def record_audio(self):
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        self.listener = self.recorder.listen_in_background(self.source, self.audio_callback, phrase_time_limit=self.record_timeout)
        self.log("Model Loaded.\n")
        
    # Callback function for the audio stream. Runs every time new audio is available.
    def audio_callback(self, _, audio:sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.data_queue.put(data)
    
    # Remove silent audio utilizing VAD (Voice Activation Detection)
    def remove_silence_VAD(self, audio_array):
        if len(audio_array) == 0 or np.max(np.abs(audio_array)) == 0:
            self.log("Input audio is silent or empty. Returning empty array.")
            return np.array([])
        
        non_silent_indices = []

        for start in range (0, len(audio_array), self.frame_size):
            # Ensure the end index does not exceed the array size
            end = min(start + self.frame_size, len(audio_array))
            frame = audio_array[start:end]

            # Ensure frame has the correct size
            if len(frame) < self.frame_size:
                frame = np.pad(frame, (0, self.frame_size - len(frame)), mode='constant')

            # Ensure the frame is a Numpy int16 array
            frame = (frame * 32767).astype(np.int16)

            # Check if the frame has speech
            try:
                if self.vad.is_speech(frame.tobytes(), self.sample_rate):
                    non_silent_indices.extend(range(start, end))
            except Exception as e:
                self.log(f"Error while processing frame: {e}")
            
        if not non_silent_indices:
            self.log("No non-silent audio detected!")
            return np.array([])
        
        # Convert non-silent indices to a binary mask
        mask = np.zeros(len(audio_array))
        mask[non_silent_indices] = 1

        # Use dilation to merge close segments
        smoothed_mask = scipy.ndimage.binary_dilation(mask, iterations=10)

        # Extract final non-silent audio using the smoothed mask
        final_indices = np.where(smoothed_mask == 1)[0]
        trimmed_audio = audio_array[final_indices[0]:final_indices[-1] + 1]

        # Extract non-silent audio portion
        #start_index = max(0, non_silent_indices[0])
        #end_index = min(len(audio_array), non_silent_indices[-1] + 1)
        #trimmed_audio = audio_array[start_index:end_index]

        return trimmed_audio

    def clear_chatbox(self):
        # Log the Chatbox Clear command
        self.log("Clearing chatbox and audio data queue...")
        # Clear VRC Chatbox via OSC
        self.client.send_message("/chatbox/clear", [])
        # Clear the audio data queue
        self.data_queue.queue.clear()
        self.chat_result = None
        self.timed_transcriptions = []

    # Transcribes a chunk of audio data
    def transcribe_audio(self):
        self.log("Starting transcription thread...")
        self.record_audio()

        # Store phrases along with their timestamps
        self.timed_transcriptions = []

        while self._running:
            try:
                now = datetime.now(timezone.utc)

                # Check if there is audio data in the queue
                if not self.data_queue.empty():
                    # Combine the audio data from the queue
                    audio_data = b''.join(self.data_queue.queue)
                    self.data_queue.queue.clear()

                    # Convert buffer to usable audio for the whisper model
                    # Converts the audo from 16 bit to 32 bit and then clamps the audo stream frequency to PCM wavelenght compatible default of 32768hz max
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    # Utilize VAD model to detect voice
                    trimmed_audio = self.remove_silence_VAD(audio_np)

                    if len(trimmed_audio) > 0:
                        self.log("Audio detected, beginning transcription!")
                        result = self.model.transcribe(trimmed_audio, word_timestamps=True, temperature=0.0, beam_size=5, language="en", task="transcribe", fp16=torch.cuda.is_available())
                        transcribed_text = result['text'].strip()
                        if transcribed_text.lower() in ['thank you.', 'you', 'thank you very much.']:
                            self.log(f"Whisper likely hallucinating, result not sent: {transcribed_text}")
                        else:
                            self.timed_transcriptions.append((now, transcribed_text))

                        # Concatenate all phrases for chatbox display
                        self.chat_result = ' '.join([t[1] for t in self.timed_transcriptions]).strip()

                        if self.chat_result:
                            self.chatbox(self.chat_result)
                        else:
                            self.log("Chat result empty.")
                    else:
                        self.log("Audio was entirely silent or below the threshold.")
                else:
                    sleep(0.25)

                self.timed_transcriptions = [
                    (timestamp , phrase) for timestamp, phrase in self.timed_transcriptions 
                    if now - timestamp < timedelta(seconds=15)
                ]

            except Exception as e:
                self.log(f"Error in processing audio: {e}")
                sleep(1) 
            except Empty:
                continue  # If the queue is empty, keep waiting for new audio chunks
            except KeyboardInterrupt:
                self.log("Transcription stopped.")
                break
        self.log("Transcription Stopped Gracefully.")
    
    def start(self):
        self.log("Initializing audio stream...")
        self._running = True
        self.thread = threading.Thread(target=self.transcribe_audio)
        self.thread.start()
                
    def stop(self):
        self.log("Stopping Recording and transcription.")
        if self._running:
            self._running = False
            if self.listener is not None:
                self.listener()
                self.listener = None
                self.log("Recording and Transcription stop.")
                #self.thread.join() # Causes application to crash.
            else:
                self.log("No active recording to stop.")
        else:
            self.log("No active Transcription process running.")
            
    # Function to send recognized text to VRChat chatbox
    def chatbox(self, text):
        self.log(f"Sending text to chatbox: {text}")
        # Send the recognized text to the chatbox
        self.client.send_message("/chatbox/input", [text, True])

if __name__ == "__main__":
    #init class
    whisp = STTOSCWhisper(whisper_model='small',sample_rate=16000)
    whisp.start()
