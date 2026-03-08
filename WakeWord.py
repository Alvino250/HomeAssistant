from microphone_input import transcribe
import re
def Word():
    lang = " "
    wakeword = "HELLO JARVIS"
    pwakeword = " "
    while(wakeword != pwakeword):   
        pwakeword, language = transcribe(language="en")
        pwakeword = pwakeword.upper()
        pwakeword = re.sub(r'[^\w\s]', '', pwakeword)
        pwakeword = pwakeword.split()
        if "MALTESE" in pwakeword:
            lang = "mt"
        elif "ENGLISH" in pwakeword:
            lang = "en"
        for i in range(len(pwakeword) - 1):
            if pwakeword[i] == "HELLO" and pwakeword[i+1] == "JARVIS":
                pwakeword = "HELLO JARVIS"
        print(repr(pwakeword))
    print("Wake word has been said")
    return lang
    