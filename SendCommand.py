import requests

def sendCommand(eid: str, dom: str, action: str):
    BASE = "http://homeassistant.local:8123"
    TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhMTU0N2YxNWM2NWQ0ZmEwYmYyNmExN2YyY2UwNjAzNyIsImlhdCI6MTc1ODgyOTIxNCwiZXhwIjoyMDc0MTg5MjE0fQ.XSNgMgfpC8Ix9mwx0lJgeh-opLKbckPPDErRAynKYgM"
    DOMAIN = dom # DOMAIN 
    url = f"{BASE}/api/services/{DOMAIN}/{action}"
    headers = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {"entity_id": eid}

    r = requests.post(url, headers=headers, json=payload)
    r.raise_for_status()  # raise exception if call fails
