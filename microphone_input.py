import speech_recognition as sr
from faster_whisper import WhisperModel

print("Loading Whisper Model (turbo)...")
model = WhisperModel("turbo", device = "auto", compute_type="float16")
print("Whisper Model has been successfully loaded")
def transcribe():
    # Initialize recognizer and Whisper model
    r = sr.Recognizer()
    r.pause_threshold = 3
    r.non_speaking_duration = 0.8
    r.dynamic_energy_threshold = True
    r.energy_threshold = 200
    with sr.Microphone() as source: # with is being used to then close the microphone source after its use
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

    
    






