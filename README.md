# avrcSTT - Another VRC Speech To Text
A learning project for myself to create a speech to text application for VRC

**Prerequisites:**

- Install python libraries
```
  pip install python-osc setuptools SpeechRecognition pyaudio whisper numpy sounddevice noisereduce scipy
```
- Install ffmpeg for whisper
```
# Linux
sudo apt update && sudo apt install ffmpeg

# MacOS
brew install ffmpeg

# Windows
chco install ffmpeg
```

**Features:**

File: SpeechToTextOSC.py 

- Utilizes Google SpeechRecognition to transcribe audio from the microphone and insert the transcribed audio into VRC via the OSC protocol.

File: SpeechToTextOSCWhisper.py 

- Utilizes Openai Whisper to transcribe audio from the microphone and insert the transcribed audio into VRC via the OSC protocol.

**Todo:**

- Process audio files to reduce background noise and improve quality
- Log Transcribes to local db maybe utilizing sqllite
- Create function to capture game audio
- Create function to process game audio and translate
