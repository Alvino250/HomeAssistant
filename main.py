from microphone_input import transcribe
from userInput import preProcess
from IntentLLM import gemma
from SendCommand import sendCommand
from spotify import extractSpotify
def main():
    #while(True):
        text = transcribe()  # Call the transcribe function to get the text from microphone input
        text = preProcess(text)  # Preprocess the transcribed text
        eid, domain, action, parsed = gemma(text)
        if "spotify" in eid:
            print("Spotify program")
            extractSpotify(parsed)
        else:
            sendCommand(eid, domain, action)
        
    # Take action based on the predicted intent
    
main()
