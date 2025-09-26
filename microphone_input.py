import speech_recognition as sr
import whisper  # Correct import for OpenAI Whisper

def transcribe():
    # Initialize recognizer and Whisper model
    r = sr.Recognizer()
    model = whisper.load_model("base")

    with sr.Microphone() as source:
        print("Say something...")
        audio = r.listen(source)

        # Save the audio to a WAV file
        with open("temp.wav", "wb") as f:
            f.write(audio.get_wav_data())

    # Transcribe using Whisper
    result = model.transcribe("temp.wav", fp16=False, language="en")
    print("Transcription:", result["text"])
    return result["text"]

