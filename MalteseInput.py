import whisper
import speech_recognition as sr
model = whisper.load_model("turbo")
r = sr.Recognizer()
with sr.Microphone() as source:
    print("Say Something")
    audio = r.listen(source)
    with open("MalteseTemp.wav", "wb") as f:
        f.write(audio.get_wav_data())

result = model.transcribe("MalteseTemp.wav", fp16=False, language="mt")
print(result["text"])    






    

    


