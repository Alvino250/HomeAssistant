from WakeWord import Word
from microphone_input import transcribe
from userInput import preProcess
from IntentLLM import gemma, loadModelAsync, ready
from SendCommand import sendCommand
from spotify import extractSpotify
import threading
import time
def main():
    #wakeword = "Hello Jarvis"
    #while(wakeword != pwakeword):   
        #pwakeword = transcribe()
        #print("Wake word has been said")
    threading.Thread(target=loadModelAsync, daemon=True).start()
    
    while not ready():
        print("LLM is getting ready...")
        time.sleep(2)
    print("Assistant is Ready")
    
    while(True):
        
        language = Word()
        if language == " ":
            language = "en"
        print("is this me", language)
        text, lang = transcribe(language)  # Call the transcribe function to get the text from microphone input
        text = preProcess(text)  # Preprocess the transcribed text
        eid, domain, action, parsed = None, None, None, None
        print(lang)
        
        #text = "Play a song from my playlist Dark/Alt Pop"
        try:
            eid, domain, action, parsed = gemma(text)
        except:
            continue
        if "spotify" in eid or action == "play_media":
            if parsed and isinstance(parsed.get("services"), dict): # line to get a list of dictionaries (chatgpt was used to assist)
                newList = []
                for k, v in parsed["services"].items():
                    if isinstance(v,dict):
                        newList.append({"service": k, **v}) # **v is used to unpack the dictionary 
                
                parsed["services"] = newList
            
            print("Spotify program")
            extractSpotify(parsed)
        elif eid and domain and action:
            sendCommand(eid, domain, action)
        else:
            print("....No idea what you said boss")
        
    # Take action based on the predicted intent
    
main()
