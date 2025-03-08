import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
from dotenv import load_dotenv
import pygame
import requests
import json
import re
import google.generativeai as genai
from langdetect import detect, DetectorFactory
import langid

# Set seed for consistent language detection
DetectorFactory.seed = 0

# Initialize pygame for audio playback
pygame.mixer.init()

load_dotenv()

# Common English words that strongly indicate English
ENGLISH_INDICATORS = [
    'the', 'is', 'are', 'was', 'were', 'this', 'that', 'these', 'those', 'a', 'an',
    'and', 'or', 'but', 'if', 'of', 'for', 'with', 'about', 'against', 'between',
    'into', 'through', 'during', 'before', 'after', 'above', 'below', 'from', 'up',
    'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'not', 'only',
    'own', 'same', 'so', 'than', 'too', 'very'
]

def is_devanagari(text):
    """Check if text contains Devanagari script (used for Hindi)."""
    devanagari_pattern = re.compile(r'[\u0900-\u097F]')
    return bool(devanagari_pattern.search(text))

def contains_english_indicators(text):
    """Check if text contains common English words/particles."""
    text_lower = text.lower().split()
    count = 0
    for word in text_lower:
        if word in ENGLISH_INDICATORS:
            count += 1
    return count

def speech_to_text():
    """Capture speech and convert to text - with English bias."""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    
    with microphone as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source)
        print("Say something!")
        audio = recognizer.listen(source)
        print("Processing speech...")
    
    # First try to recognize as English (giving it preference)
    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print(f"English recognition result: {text}")
        
        # Check if the recognized text has strong English indicators
        english_word_count = contains_english_indicators(text)
        if english_word_count >= 2:
            print(f"Found {english_word_count} English indicators, confirming as English")
            return text, 'en'
            
        # If the text contains Devanagari, it's definitely Hindi
        if is_devanagari(text):
            print("Text contains Devanagari script - confirming as Hindi")
            return text, 'hi'
            
        # Otherwise, still assume English but check more thoroughly
        return text, 'en'
        
    except Exception as e:
        print(f"English recognition failed: {e}")
        
        # If English recognition failed, try Hindi
        try:
            text = recognizer.recognize_google(audio, language="hi-IN")
            print(f"Hindi recognition result: {text}")
            return text, 'hi'
        except Exception as e:
            print(f"Hindi recognition also failed: {e}")
            return None, None

def translate_text(text, source_lang, target_lang):
    """Translate text from source_lang to target_lang."""
    if source_lang == target_lang:
        return text
        
    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translation = translator.translate(text)
        print(f"Translated ({source_lang} → {target_lang}): {translation}")
        return translation
    except Exception as e:
        print(f"Translation error: {e}")
        return text  # Return original text if translation fails

# Read the API key from the environment variable
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API key not found. Please set the GEMINI_API_KEY environment variable.")

print("API key found. Initializing Gemini API...")

genai.configure(api_key=api_key)

def clean_text(text):
    """Removes special characters except spaces, letters, and numbers."""
    return re.sub(r"[^a-zA-Z0-9\s]", "", text)  # Removes special characters

def generate_response_with_gemini(text, max_tokens=100):
    """Generate a concise response using Google's Gemini API."""
    print("Generating response using Gemini-2 Flash...")

    prompt = (
        "Provide a well-structured and informative response. "
        "Ensure clarity while adding relevant details, explanations, or examples. "
        "Keep the response natural and suitable for spoken conversation. "
        "Do not use special characters, symbols, or emojis. "
        "Here is the input: " + text
    )

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(
            prompt,
            generation_config={
                "max_output_tokens": max_tokens,
                "temperature": 0.7,
                "top_p": 0.9
            }
        )

        if hasattr(response, "text"):
            cleaned_response = clean_text(response.text)
            return cleaned_response
        else:
            print("Unexpected response format:", response)
            return "Error generating response."
    except Exception as e:
        print(f"Exception: {e}")
        return "I couldn't generate a response at this time."

def text_to_speech(text, lang):
    """Convert text to speech in the specified language."""
    temp_file = "response.mp3"
    
    tts = gTTS(text=text, lang=lang, slow=False)
    tts.save(temp_file)
    
    # Play the audio
    pygame.mixer.music.load(temp_file)
    pygame.mixer.music.play()
    
    # Wait for audio to finish playing
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    
    # Clean up
    pygame.mixer.music.unload()
    os.remove(temp_file)

def main():
    # 1. Speech to text with English bias
    text, detected_language = speech_to_text()
    if not text:
        print("Speech recognition failed")
        return
    
    print(f"Using recognized text: '{text}' (detected as {detected_language})")
    
    # 2. Double-check language if needed
    if detected_language == 'hi':
        # Verify if there are English indicators in the text
        english_indicators = contains_english_indicators(text)
        if english_indicators >= 3:
            print(f"Found {english_indicators} strong English indicators in 'Hindi' text, switching to English")
            detected_language = 'en'
    
    # 3. Translate to English if not already in English
    if detected_language == "hi":
        english_text = translate_text(text, source_lang="hi", target_lang="en")
    else:
        english_text = text
    
    # 4. Generate response with Gemini API
    response_text = generate_response_with_gemini(english_text)
    print(response_text)
    
    # 5. Translate response back to original language if needed
    if detected_language == "hi":
        translated_response = translate_text(response_text, source_lang="en", target_lang="hi")
    else:
        translated_response = response_text
    
    # 6. Convert response to speech and play it
    text_to_speech(translated_response, lang=detected_language)
    print("Response audio played.")

if __name__ == "__main__":
    main()