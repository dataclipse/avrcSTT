import whisper, speech_recognition as sr, numpy as np, warnings, torch, threading
from sys import platform
from pythonosc import udp_client
from queue import Queue, Empty
from datetime import datetime, timedelta, timezone
from time import sleep

# Suppress future and user warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class STTOSCWhisper:
    def __init__(self, whisper_model='small', sample_rate=16000, log_callback=None):
    
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
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def record_audio(self):
        with self.source:
            self.recorder.adjust_for_ambient_noise(self.source)
        self.listener = self.recorder.listen_in_background(self.source, self.audio_callback, phrase_time_limit=self.record_timeout)
        self.log("Model Loaded.\n")
        #print("Model Loaded.\n")

    # Callback function for the audio stream. Runs every time new audio is available.
    def audio_callback(self, _, audio:sr.AudioData) -> None:
        data = audio.get_raw_data()
        self.data_queue.put(data)

    def rms_energy(self, audio_array):
        return np.sqrt(np.mean(np.square(audio_array)))
    
    def zero_crossing_rate(self, window):
        zcr = np.mean(np.abs(np.diff(np.sign(window))))  # Calculate zero-crossing rate
        return zcr
    
    def remove_silence(self, audio_array, sample_rate=16000, window_size=5):
        # Define the window size in frames
        window_length = int(sample_rate * window_size)
        
        if np.max(np.abs(audio_array)) == 0:
            self.log("Input audio is silent. Returning empty array.")
            #print("Input audio is silent. Returning empty array.")
            return np.array([])
        
        # Normalize audio to the range [-1, 1] for consistent energy calculations
        normalized_audio = audio_array / np.max(np.abs(audio_array))

        mean_energy = np.mean(np.abs(normalized_audio))
        energy_threshold = mean_energy * 0.5

        # Store indices of non-silent windows
        non_silent_indices = []

        # Slide the window across the audio signal
        for start in range(0, len(normalized_audio), window_length):
            window = normalized_audio[start:start + window_length]
            
            # Calculate RMS energy for the current window
            energy = self.rms_energy(window)

            zcr = self.zero_crossing_rate(window)
            # Check if the window contains meaningful audio
            if energy >= energy_threshold and zcr > 0.1:
                non_silent_indices.extend(range(start, start + len(window)))

        if len(non_silent_indices) == 0:
            self.log("No non-silent audio detected!")
            #print("No non-silent audio detected!")
            return np.array([])  # Return an empty array if all audio is silent

        # Extract the non-silent portion of the audio
        start_index = max(0, non_silent_indices[0])
        end_index = min(len(audio_array), non_silent_indices[-1] + 1)
        trimmed_audio = audio_array[start_index:end_index]
        return trimmed_audio
    
    # Transcribes a chunk of audio data
    def transcribe_audio(self):
        self.log("Starting transcription thread...")
        #print("Starting transcription thread...")
        self.record_audio()
        while self._running:
            try:
                now = datetime.now(timezone.utc)
                # Check if there is audio data in the queue
                if not self.data_queue.empty():
                    phrase_complete = False

                    # Check if the timeout for phrase completion has passed
                    if self.phrase_time and now - self.phrase_time > timedelta(seconds=self.phrase_timeout):
                        phrase_complete = True
                    
                    # Set phrase time to current timestamp
                    self.phrase_time = now

                    # Combine the audio data from the queue
                    audio_data = b''.join(self.data_queue.queue)
                    self.data_queue.queue.clear()

                    # Convert buffer to usable audio for the whisper model
                    # Converts the audo from 16 bit to 32 bit and then clamps the audo stream frequency to PCM wavelenght compatible default of 32768hz max
                    audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    trimmed_audio = self.remove_silence(audio_np)

                    if len(trimmed_audio) > 0:
                        self.log("Non-silent audio found, ready for further processing!")
                        #print("Non-silent audio found, ready for further processing!")
                        result = self.model.transcribe(trimmed_audio, temperature=0.0, beam_size=5, language="en", task="transcribe", fp16=torch.cuda.is_available())
                        transcribed_text = result['text'].strip()

                        if phrase_complete:
                            self.transcription = [transcribed_text]
                        else:
                            if self.transcription:
                                self.transcription[-1] = transcribed_text
                            else:
                                self.transcription.append(transcribed_text) 
                        # Concatenate the transcription lines into a single string
                        chat_result = ' '.join(self.transcription).strip()
                        if chat_result:
                            if chat_result == 'Thank you.' or chat_result == 'You' or chat_result == 'you':
                                self.log(f"Whisper likely hallucinating, result not sent: {chat_result}")
                                #print(f"Whisper likely hallucinating, result not sent: {chat_result}")
                            else:
                                #self.log(chat_result)
                                #print(chat_result)
                                # Send the result to the VRC
                                self.chatbox(chat_result)
                        else:
                            self.log("Chat result empty.")
                            #print("Chat result empty.")
                    else:
                        self.log("Audio was entirely silent or below the threshold.")
                        #print("Audio was entirely silent or below the threshold.")
                else:
                    sleep(0.25)
            except Exception as e:
                self.log(f"Error in processing audio: {e}")
                #print(f"Error in processing audio: {e}")
                sleep(1) 
            except Empty:
                continue  # If the queue is empty, keep waiting for new audio chunks
            except KeyboardInterrupt:
                self.log("Transcription stopped.")
                #print("Transcription stopped.")
                break
        self.log("Transcription Stopped Gracefully.")
    
    def start(self):
        self.log("Initializing audio stream...")
        #print("Initializing audio stream...")
        self._running = True
        self.thread = threading.Thread(target=self.transcribe_audio)
        self.thread.start()
        #self.transcribe_audio()
        
    def stop(self):
        self.log("Stopping Recording and transcription.")
        if self._running:
            self._running = False
            if self.listener is not None:
                self.listener()
                self.listener = None
                self.log("Recording and Transcription stop.")
                #self.thread.join()
            else:
                self.log("No active recording to stop.")
        else:
            self.log("No active Transcription process running.")
            
    # Function to send recognized text to VRChat chatbox
    def chatbox(self, text):
        self.log(f"Sending text to chatbox: {text}")
        #print(f"Sending text to chatbox: {text}")
        # Send the recognized text to the chatbox
        self.client.send_message("/chatbox/input", [text, True])

if __name__ == "__main__":
    #init class
    whisp = STTOSCWhisper(whisper_model='small',sample_rate=16000)
    whisp.start()
