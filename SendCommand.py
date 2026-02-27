import requests

def sendCommand(eid: str, dom: str, action: str):
    BASE = "http://homeassistant.local:8123"
    TOKEN = ""
    DOMAIN = dom # DOMAIN 
    url = f"{BASE}/api/services/{DOMAIN}/{action}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"entity_id": eid}

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()  # raise exception if call fails
