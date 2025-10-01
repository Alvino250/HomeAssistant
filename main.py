from microphone_input import transcribe
from userInput import preProcess
from IntentLLM import gemma
from SendCommand import sendCommand
def main():
    #while(True):
        text = transcribe()  # Call the transcribe function to get the text from microphone input
        text = preProcess(text)  # Preprocess the transcribed text
        eid = gemma(text)
        sendCommand(eid)
        
    # Take action based on the predicted intent
    
main()
