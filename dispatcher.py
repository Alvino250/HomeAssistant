from actions import turn_on_lights, turn_off_lights, turn_on_tv, turn_off_tv, query_weather, general_greeting, fallback_action
from G4F import g4fReply 
intent_dispatcher = {
    'TurnOnLights': turn_on_lights,
    'TurnOffLights': turn_off_lights,
    'TurnOnTV': turn_on_tv,
    'TurnOffTV': turn_off_tv,
    'QueryWeather': query_weather,
    'GeneralGreeting': general_greeting,
    'Fallback': fallback_action
}

def handle_intent(intent, user_input=None):
    """
    Dispatches the intent to the corresponding action function.
    
    Args:
        intent (str): The intent to handle.
        
    Returns:
        str: The response from the action function.
    """
    action = intent_dispatcher.get(intent, fallback_action)
    if intent == "OutOfScope" and user_input is not None:
       return g4fReply(user_input)
    return action()  # Call the action function and return its response
