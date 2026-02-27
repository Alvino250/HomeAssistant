# Use a pipeline as a high-level helper
from transformers import pipeline

pipe = pipeline("automatic-speech-recognition", model="carlosdanielhernandezmena/whisper-largev2-maltese-8k-steps-64h")

