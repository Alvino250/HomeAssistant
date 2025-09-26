from microphone_input import transcribe
from userInput import preProcess
from IntentLLM import gemma
def main():
    #while(True):
        text = transcribe()  # Call the transcribe function to get the text from microphone input
        text = preProcess(text)  # Preprocess the transcribed text
        gemma(text)
        
    # Take action based on the predicted intent
    
main()
