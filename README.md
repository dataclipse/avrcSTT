# avrcSTT

- Install libraries
```
  pip install python-osc setuptools SpeechRecognition pyaudio
```
- Included setuptools due to SpeechRecognition requiring a deprecated function 'distutils'
- Test connections to VRC via OSC
- Create function for recognizing speech
- Create function for sending text to vrc text box
- Create function to display messages as notifications
- Added overlay to display messages for the user.
- Altered most functions to enable async calling

Todo:
- Create function to capture game audio
- Create function to process game audio and translate
