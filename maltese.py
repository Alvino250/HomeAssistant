from transformers import pipeline
import speech_recognition as sr

pipe = pipeline("automatic-speech-recognition", model="carlosdanielhernandezmena/whisper-largev2-maltese-8k-steps-64h", device=0)

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
        with open("temp2.wav", "wb") as f:
            f.write(audio.get_wav_data())
            
            
transcribe()
result = pipe("temp2.wav")
print(result["text"])
