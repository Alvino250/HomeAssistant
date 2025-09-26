import joblib
import re
from dispatcher import handle_intent  # Assuming this is a module that handles the intent after prediction 
import edge_tts
import asyncio
import subprocess

# Remove Punctuation etc as it is irrelevant for intent classification
def preProcess(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)      # Remove digits
    text = text.lower()                  # Convert to lowercase
    return text 

def userInput():
    user_input = input("Enter your command: ")
    processed_input = preProcess(user_input)
    return processed_input

def predict_intent(user_input,):
    threshold = 0.9
    # Load the trained model
    model = joblib.load('intent_classifier.pkl')  # Load the trained model
    # Predict the intent of the user input
    probs = model.predict_proba([user_input])[0]  # Get the probabilities of each class
    max_prob = max(probs)  # Get the maximum probability
    print(f"Probabilities: {probs}")  # Print the probabilities for debugging
    if max_prob < threshold:
        intent = "OutOfScope"
    else:
        intent = model.classes_[probs.argmax()]  # Get the class with the highest probability
    intentText = handle_intent(intent, user_input)  # Handle the intent using the dispatcher
    print(intentText)  # Print the predicted intent
    asyncio.run(speak(intentText))
    return intent

async def speak(action):
    communicate = edge_tts.Communicate(text=action, voice="en-US-GuyNeural")
    await communicate.save("output.mp3")
    subprocess.run(["mpg123", "output.mp3"])  # Play the audio file using mpg123




#input = userInput()  # Get user input
#preProcess(input)  # Preprocess the input
#predicted_intent = predict_intent(input)  # Predict the intent
#print(f"Predicted Intent: {predicted_intent}")  # Print the predicted intent
#handled_intent = handle_intent(predicted_intent)  # Handle the intent (this could be a function call to handle the intent)
#print(f"Handled Intent: {handled_intent}")  # Print the handled intent

