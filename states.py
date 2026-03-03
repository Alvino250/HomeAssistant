import requests

def states(timeout = 8):
    BASE = "http://homeassistant.local:8123"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhMTU0N2YxNWM2NWQ0ZmEwYmYyNmExN2YyY2UwNjAzNyIsImlhdCI6MTc1ODgyOTIxNCwiZXhwIjoyMDc0MTg5MjE0fQ.XSNgMgfpC8Ix9mwx0lJgeh-opLKbckPPDErRAynKYgM"

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
    

