
# Imports the Google Cloud client library

from google.cloud import speech
import creds
import os

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = creds.GOOGLE_JSON_PATH
def run_quickstart() -> speech.RecognizeResponse:
    # Instantiates a client
    client = speech.SpeechClient()

    client = speech.SpeechClient()

    # Read the content of the local audio file
    with open('output2.mp3', "rb") as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="pt-BR",
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")



import sounddevice as sd
import numpy as np
import keyboard
from pydub import AudioSegment

def record_audio(duration=10, sample_rate=44100):
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=2, dtype=np.int16)
    sd.wait()
    return recording

def save_as_mp3(audio_data, filename='output2.mp3', sample_width=2, channels=2, sample_rate=44100):
    audio_segment = AudioSegment(
        audio_data.tobytes(),
        frame_rate=sample_rate,
        sample_width=sample_width,
        channels=channels
    )
    audio_segment.export(filename, format='mp3')

def main():
    print("Press 'P' to start recording. Press 'Q' to stop and save as MP3.")
    
    is_recording = False
    recording_data = []

    while True:
        if keyboard.is_pressed('p') and not is_recording:
            print("Recording...")
            is_recording = True
            recording_data = record_audio()

        if keyboard.is_pressed('q') and is_recording:
            print("Stopping recording and saving as MP3...")
            is_recording = False
            save_as_mp3(np.concatenate(recording_data))
            print("Saved as MP3: output2.mp3")
            run_quickstart()
            break

if __name__ == "__main__":
    main()
