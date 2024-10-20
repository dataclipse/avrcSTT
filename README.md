### **Release Notes for avrcSTT - Another VRC Speech to Text**
**Version 0.0.11**

**Overview:** avrcSTT is an application designed to enhance your communication experience in VRC. By seamlessly transcribing live audio into text, avrcSTT allows users who do not wish to communicate vocally to engage in chats without the need for manual typing, making interactions more fluid and accessible.

### **Key Features:**

**Live Audio Transcription:** Captures real-time audio and converts it to text for instant chat integration.

**VRC Integration:** Directly inserts transcribed text into the VRC chatbox for effortless communication.

### Improvements and Fixes:

Initial release of the application with robust functionality for real-time audio processing and transcription.

### **Future Plans:**

Configurable Settings: Customize recording duration, audio source, and transcription preferences to suit your needs.
Enhanced accuracy of transcription through optimized audio processing techniques.

### **Known Issues:**

The application may experience delays in transcription for longer phrases or in noisy environments. Future updates will focus on improving accuracy and performance.
The application utilizes the OpenAI whisper model so it is prone to hallucinations.  (Future releases will aim to reduce the hallucination frequency) 

### **Getting Started:**

### **Precompiled:**

**Installation:** Download the application from 7z file.

**Setup:** Extract the avrcSTT folder to your preferred location.

**Launch:** Start the application (avrcSTT.exe) after the application loads select the 'Start STT' button and when the model has finished loading speak to see your words transcribed into the VRC chatbox!

### **Build from Source:**

**Dependencies:**
Install Python 3.10 or greater
https://www.python.org/downloads/

After installing Python run the following from command line to install all the library dependencies
```
pip install pywinstyles sv_ttk openai-whisper SpeechRecognition python-osc torch pyaudio webrtcvad scipy
```

**Launch:** The main file can be executed by running
```
python avrcstt.py
```

### **Feedback and Support:**

Please report any issues or suggestions to dataclipsedev@gmail.com.
