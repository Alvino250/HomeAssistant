import speech_recognition as sr
from faster_whisper import WhisperModel
from transformers import pipeline

print("Loading Whisper Model (turbo)...")
model = WhisperModel("turbo", device = "auto", compute_type="float16")
pipe = pipeline("automatic-speech-recognition", model="carlosdanielhernandezmena/whisper-largev2-maltese-8k-steps-64h")
print("Whisper Model has been successfully loaded")
def transcribe(language : str | None = None) -> tuple[str,str]:
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
    if language == 'mt':
        segments = pipe("temp.wav")
    else:
        segments, info = model.transcribe("temp.wav", language=language, vad_filter=True) # Voice Activation Detection Filter  --> Reduces Hallucinations
    
    fullText = ""
    
    for x in segments:
        fullText += x.text.strip() + " "
    print("Transcription:", fullText)
    print("Language")
    return fullText, language

    
    






