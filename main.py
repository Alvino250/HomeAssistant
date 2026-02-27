from microphone_input import transcribe
from userInput import preProcess
from IntentLLM import gemma, loadModelAsync, ready
from SendCommand import sendCommand
from spotify import extractSpotify
import threading
import time
def main():
    #while(True):
        text = transcribe()  # Call the transcribe function to get the text from microphone input
        threading.Thread(target=loadModelAsync, daemon=True).start()
        text = preProcess(text)  # Preprocess the transcribed text
        eid, domain, action, parsed = None, None, None, None
        while not ready():
            print("LLM is getting ready...")
            time.sleep(2)
        #text = "Play a song from my playlist Dark/Alt Pop"
        eid, domain, action, parsed = gemma(text)
        if "spotify" in eid or action == "play_media":
            print("Spotify program")
            extractSpotify(parsed)
        else:
            sendCommand(eid, domain, action)
        
    # Take action based on the predicted intent
    
main()
