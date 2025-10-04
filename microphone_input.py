import speech_recognition as sr
from faster_whisper import WhisperModel

def transcribe():
    # Initialize recognizer and Whisper model
    r = sr.Recognizer()
    model = WhisperModel("turbo", device = "auto", compute_type="float16")

    with sr.Microphone() as source:
        print("Say something...")
        audio = r.listen(source)

        # Save the audio to a WAV file
        with open("temp.wav", "wb") as f:
            f.write(audio.get_wav_data())

    # Transcribe using Whisper
    segments, info = model.transcribe("temp.wav", language="en")
    fullText = ""
    for x in segments:
        fullText += x.text.strip() + " "
    print("Transcription:", fullText)
    return fullText






