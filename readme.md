# ASR_TTS

This project is an Automatic Speech Recognition (ASR) and Text-to-Speech (TTS) system that recognizes speech, translates it if necessary, generates a response using Google's Gemini API, and converts the response back to speech.

## Features

- Speech recognition with a bias towards English.
- Language detection and translation between English and Hindi.
- Response generation using Google's Gemini API.
- Text-to-speech conversion for the generated response.

## Requirements

- Python 3.7+
- See `requirements.txt` for the list of required Python packages.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/avinash4002/ASR_TTS.git
    cd ASR_TTS
    ```

2. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

3. Set up the environment variable for the Gemini API key:
    ```sh
    export GEMINI_API_KEY=your_api_key_here
    ```

## Usage

Run the main script:
```sh
python [app.py](http://_vscodecontentref_/1)