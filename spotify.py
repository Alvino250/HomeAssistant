import re
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

BASE = "http://homeassistant.local:8123"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJhMTU0N2YxNWM2NWQ0ZmEwYmYyNmExN2YyY2UwNjAzNyIsImlhdCI6MTc1ODgyOTIxNCwiZXhwIjoyMDc0MTg5MjE0fQ.XSNgMgfpC8Ix9mwx0lJgeh-opLKbckPPDErRAynKYgM"

SPOTIFY_ENTITY_ID = "media_player.spotify_alvin_grima"

# 🔑 Your Spotify developer credentials (inline)
CLIENT_ID = "0ca407636f0a463a9096e45930b5ace2"
CLIENT_SECRET = "3a5e33ec865949f59cdcb3037405da03"

def extractSpotify(parsed: dict) -> None:
    """Parsed is the LLM JSON dict. Extract and call HA to play."""
    services = parsed.get("services") or []
    if not isinstance(services, list) or not services:
        raise ValueError("No services in parsed reply")

    svc = services[0]
    eid   = svc.get("entity_id")
    query = svc.get("query")
    kind  = (svc.get("kind") or "track").lower()
    source = svc.get("source")

    if not eid:
        raise ValueError("Missing entity_id in services[0]")
    if not query:
        raise ValueError("Missing query (what to play) in services[0]")

    # Always target Spotify entity
    if not eid.startswith("media_player.spotify"):
        eid = SPOTIFY_ENTITY_ID

    # Optional: pick output device first
    if source:
        select_source(eid, source)
    else:
        ensure_active_device(eid)

    # Map kind → HA media_content_type
    media_type = {
        "track": "music",
        "album": "album",
        "playlist": "playlist",
        "artist": "artist"
    }.get(kind, "music")

    # 🎯 Resolve Spotify URI first (always)
    uri = search_spotify_uri(query, kind)
    if uri:
        query = uri

    print("We made it till here")
    play_media(eid, media_content_id=query, media_content_type=media_type, kind=kind)


def select_source(entity_id: str, source: str) -> None:
    """Select Spotify Connect output device (TV, speaker, etc.)."""
    url = f"{BASE}/api/services/media_player/select_source"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = {"entity_id": entity_id, "source": source}
    r = requests.post(url, headers=headers, json=body, timeout=10)
    if r.status_code // 100 != 2:
        print("select_source FAILED:", r.status_code, r.text)
        r.raise_for_status()


def ensure_active_device(entity_id: str) -> None:
    """Pick the first available Spotify Connect device if none selected."""
    sources = get_source_list(entity_id)
    if not sources:
        return
    try:
        select_source(entity_id, sources[1])
    except Exception:
        pass


def get_source_list(entity_id: str) -> list[str]:
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.get(f"{BASE}/api/states/{entity_id}", headers=headers, timeout=8)
    if r.status_code // 100 != 2:
        return []
    return r.json().get("attributes", {}).get("source_list", []) or []


def _ensure_uri(s: str) -> str | None:
    """Return spotify: URI if string already is a Spotify link."""
    s = (s or "").strip()
    if s.startswith("spotify:"):
        return s
    m = re.match(r"https?://open\.spotify\.com/([a-z]+)/([A-Za-z0-9]+)", s)
    if m:
        kind, sid = m.group(1), m.group(2)
        return f"spotify:{kind}:{sid}"
    return None


def search_spotify_uri(query: str, kind: str = "track") -> str | None:
    """Convert text like 'Bag of Bones by Lord Huron' → Spotify URI."""
    uri = _ensure_uri(query)
    if uri:
        return uri

    print(f"Searching Spotify for: '{query}' ({kind})")

    sp = spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET
        )
    )

    # Try to separate title and artist for better accuracy
    parts = re.split(r"\bby\b", query, flags=re.IGNORECASE)
    if len(parts) >= 2:
        title, artist = parts[0].strip(), parts[1].strip()
        q = f'track:"{title}" artist:"{artist}"'
    else:
        q = query

    res = sp.search(q=q, type=kind, limit=1, market="MT")
    items = res.get(f"{kind}s", {}).get("items", [])
    if items:
        uri = items[0]["uri"]
        print(f"Found URI: {uri}")
        return uri

    print("No URI found for:", query)
    return None


def play_media(entity_id: str, media_content_id: str, media_content_type: str, *, kind: str = "track") -> None:
    """Send play_media command to Home Assistant."""
    url = f"{BASE}/api/services/media_player/play_media"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = {
        "entity_id": entity_id,
        "media_content_id": media_content_id,
        "media_content_type": media_content_type
    }

    r = requests.post(url, headers=headers, json=body, timeout=10)
    if r.status_code // 100 != 2:
        print("play_media FAILED")
        print("URL:", url)
        print("BODY:", body)
        print("STATUS:", r.status_code)
        print("RESP:", r.text)
        r.raise_for_status()
