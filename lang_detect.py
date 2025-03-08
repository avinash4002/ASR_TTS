import speech_recognition as sr
# from googletrans import Translator, LANGUAGES
from langdetect import detect

# List of common Indian languages with their short codes
INDIAN_LANGUAGES = {
    'hi': 'Hindi', 'bn': 'Bengali', 'te': 'Telugu', 'mr': 'Marathi',
    'ta': 'Tamil', 'ur': 'Urdu', 'gu': 'Gujarati', 'kn': 'Kannada',
    'ml': 'Malayalam', 'pa': 'Punjabi', 'or': 'Odia', 'as': 'Assamese',
}

def detect_language(text):
    """Detect the language of the transcribed text."""
    try:
        detected_lang = detect(text)
        return detected_lang if detected_lang in INDIAN_LANGUAGES else 'en'
    except:
        return 'en'  # Default to English if detection fails

def transcribe_speech():
    """Capture audio, detect language, and transcribe in the same language."""
    recognizer = sr.Recognizer()
    
    with sr.Microphone() as source:
        print("\nAdjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        print("🎤 Speak now...")

        try:
            audio = recognizer.listen(source, timeout=10)  # Capture audio
            print("🔄 Processing speech...")

            # Attempt recognition in multiple languages
            transcribed_text = None
            detected_language = None

            for lang in INDIAN_LANGUAGES.keys():
                try:
                    text = recognizer.recognize_google(audio, language=lang)
                    detected_language = detect_language(text)

                    # If detected language matches attempted recognition, use it
                    if detected_language == lang:
                        transcribed_text = text
                        break
                except sr.UnknownValueError:
                    continue
                except sr.RequestError:
                    print("🔴 Google API request failed.")
                    return None, None

            if transcribed_text:
                print(f"\n✅ Detected Language: {INDIAN_LANGUAGES.get(detected_language, 'Unknown')}")
                print(f"📝 Transcription: {transcribed_text}")
                return transcribed_text, detected_language
            else:
                print("\n⚠️ Could not understand the speech. Try again.")
                return None, None

        except sr.WaitTimeoutError:
            print("\n⏳ No speech detected. Try again.")
            return None, None

# Run the transcription
if __name__ == "__main__":
    transcribe_speech()
