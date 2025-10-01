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


