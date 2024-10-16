# avrcSTT - Another VRC Speech To Text
A learning project for myself to create a speech to text application for VRC

**Prerequisites:**

- Install python libraries
```
  pip install python-osc setuptools SpeechRecognition whisper numpy 
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

File: main.py 

- Launches main app gui.

File: ui_main.py 

- Builds gui for application.

File: STTOSCWhisper.py 

- Utilizes Openai Whisper to transcribe audio from the microphone and insert the transcribed audio into VRC via the OSC protocol.

**Todo:**

- Log Transcribes to local db maybe utilizing sqllite
- Tune output more to reduce hallucinations
