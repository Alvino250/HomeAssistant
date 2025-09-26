
import random
import pandas as pd

intents_templates = {'TurnOnLights': ['turn on the {room} lights', 'can you switch on the {room} lights?', 'please activate the {room} lights', 'lights on in the {room}', 'I want the {room} lights on', 'enable lighting in the {room}', 'let there be light in the {room}', 'can you turn on the lights in the {room}?', 'power up the {room} lights', 'switch on lights in the {room} now'], 'TurnOffLights': ['turn off the {room} lights', 'switch off the {room} lights', 'kill the lights in the {room}', 'I want the {room} lights off', 'deactivate lighting in the {room}', 'make it dark in the {room}', 'can you turn off the lights in the {room}?', 'cut power to the {room} lights', 'please shut off the {room} lights', 'disable lights in the {room}'], 'TurnOnTV': ['turn on the {room} TV', 'can you switch on the TV in the {room}?', 'power on the {room} television', 'enable the {room} TV', 'please activate the {room} TV', 'TV on in the {room}', 'I want to watch TV in the {room}', 'start the {room} television', 'boot up the {room} TV', 'can you put the TV on in the {room}?'], 'TurnOffTV': ['turn off the {room} TV', 'can you switch off the TV in the {room}?', 'shut down the {room} television', 'TV off in the {room}', 'disable the {room} TV', 'please deactivate the {room} TV', 'stop the {room} television', 'cut off the {room} TV', 'turn the television off in the {room}', 'I’m done with the TV in the {room}'], 'QueryWeather': ['what’s the weather like?', 'is it raining outside?', 'do I need an umbrella today?', 'is it hot today?', 'tell me today’s forecast', "what's the temperature?", "how's the weather outside?", 'any rain expected today?', "what's the forecast?", 'do I need sunglasses?'], 'GeneralGreeting': ['hello', 'hi', 'good morning', 'good evening', 'yo', 'sup', "what's up?", 'howdy', 'hey there', 'greetings']}

rooms = ['living room', 'bedroom', 'kitchen', 'office', 'garage', 'bathroom', 'dining room', 'hallway']

def generate_dataset(num_examples):
    data = []
    for _ in range(num_examples):
        intent = random.choice(list(intents_templates.keys()))
        template = random.choice(intents_templates[intent])
        if "{{room}}" in template:
            room = random.choice(rooms)
            utterance = template.format(room=room)
        else:
            utterance = template
        data.append((utterance, intent))
    return pd.DataFrame(data, columns=["utterance", "intent"])

# Example usage:    
df = generate_dataset(2000000)
df.to_csv("test.csv", index=False)
