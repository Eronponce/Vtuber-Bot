import speech_recognition as sr

def recognize_speech():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Say something:")
        recognizer.adjust_for_ambient_noise(source)

        # Flag to indicate whether speech is currently being detected
        speech_detected = False

        while True:
            try:
                audio = recognizer.listen(source, timeout=1)  # Listen for 1 second at a time
                if not audio:
                    # No speech detected in the last second
                    if speech_detected:
                        print("Pause detected.")
                        speech_detected = False
                else:
                    # Speech detected
                    speech_detected = True

                    text = recognizer.recognize_google(audio, language="pt-BR")
                    print("You said:", text)

            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Could not request results from Google Web Speech API; {e}")
            except sr.WaitTimeoutError:
                pass  # Timeout when no speech is detected, continue listening

if __name__ == "__main__":
    recognize_speech()
