import requests

def states(timeout = 8):
    BASE = "http://homeassistant.local:8123"
    TOKEN = ""

    r = requests.get(f"{BASE}/api/states",
                 headers={"Authorization": f"Bearer {TOKEN}",
                          "Content-Type": "application/json"}, timeout = timeout)
    r.raise_for_status()
    states = r.json()
    
    # Extract only entity_id + friendly_name
    devices = []
    for entity in states:
        name = entity.get("attributes", {}).get("friendly_name", entity["entity_id"])
        devices.append({"entity_id": entity["entity_id"], "name": name})

    return devices
    # print(states)  # list of entity dicts
    

