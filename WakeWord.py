from microphone_input import transcribe
import re
def Word():
    wakeword = "HELLO JARVIS"
    pwakeword = " "
    while(wakeword != pwakeword):   
        pwakeword = transcribe()
        pwakeword = pwakeword.upper()
        pwakeword = re.sub(r'[^\w\s]', '', pwakeword)
        pwakeword = " ".join(pwakeword.split())
        pwakeword = pwakeword.strip()
        print(repr(pwakeword))
    print("Wake word has been said")