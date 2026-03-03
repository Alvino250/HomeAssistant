import requests

def services(timeout = 8):
    BASE = "http://homeassistant.local:8123"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhMTU0N2YxNWM2NWQ0ZmEwYmYyNmExN2YyY2UwNjAzNyIsImlhdCI6MTc1ODgyOTIxNCwiZXhwIjoyMDc0MTg5MjE0fQ.XSNgMgfpC8Ix9mwx0lJgeh-opLKbckPPDErRAynKYgM"

    r = requests.get(f"{BASE}/api/services",
                 headers={"Authorization": f"Bearer {TOKEN}",
                          "Content-Type": "application/json"}, timeout = timeout)
    r.raise_for_status()
    services = r.json()
    
    # Extract only entity_id + friendly_name
    generic = []
    for x in services:
        if x["domain"] == "homeassistant" or x["domain"] == "light" or x["domain"] == "media_player" or x["domain"] == "climate":
            generic.append(x["services"].keys())
            
    print(generic)
    return generic
    # print(states)  # list of entity dicts
    

services()
