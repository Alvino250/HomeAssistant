import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import joblib

# Remove Punctuation etc as it is irrelevant for intent classification
def preProcess(text):
    text = re.sub(r'[^\w\s]', '', text)  # Remove punctuation
    text = re.sub(r'\d+', '', text)      # Remove digits
    text = text.lower()                  # Convert to lowercase
    return text 
def loadData(file_path):
    df = pd.read_csv(file_path) # reads csv file into a pandas DataFrame
    df['utterance'] = df['utterance'].apply(preProcess)  # Applies the preprocessing function to each row
    return df

## Create a pipeline for text classification
def createPipeline():
    model = Pipeline([
        ('vectorizer', TfidfVectorizer()),  # Converts text to TF-IDF features # converting text to numerical features
        ('classifier', LogisticRegression(max_iter=1000))  # Logistic Regression model
    ])
    return model


path = 'test.csv'  # Path to the CSV file containing intents and utterances
df = loadData(path)  # Load the data from the CSV file
df["utterance"] = df["utterance"].apply(preProcess)  # Preprocess the utterances

model = createPipeline()  # Create the model pipeline
model.fit(df["utterance"], df["intent"])  # Fit the model to the data
joblib.dump(model, 'intent_classifier.pkl')  # Save the model to a file





    
    

