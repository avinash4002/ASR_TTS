import speech_recognition as sr
from gtts import gTTS
import os

def speech_to_text():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)
    
    try:
        text = recognizer.recognize_google(audio)
        print("Recognized Text:", text)
        return text
    except sr.UnknownValueError:
        print("Could not understand the audio")
        return None
    except sr.RequestError:
        print("Could not request results, check your internet connection")
        return None
    

def text_to_speech(text, lang='en'):
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save("output.mp3")
    os.system("start output.mp3" if os.name == "nt" else "mpg321 output.mp3")


if __name__ == "__main__":
    text = speech_to_text()
    if text:
        text_to_speech(text)