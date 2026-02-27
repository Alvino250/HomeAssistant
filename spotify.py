import re
import time
import requests
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import difflib

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

    # Always play via your Spotify entity
    original_eid = eid
    if "spotify" not in str(eid).lower():
        # Use the original device name as the preferred source (strip domain; replace underscores)
        preferred_source = str(eid).split(".", 1)[-1].replace("_", " ").strip()
        # if the LLM already set 'source', keep it; else use preferred
        source = source or preferred_source
        eid = SPOTIFY_ENTITY_ID
    else:
        eid = SPOTIFY_ENTITY_ID  # normalize to your specific spotify entity

    # Optional: pick output device first
    if source:
        select_source(eid, source)
    else:
        print_spotify_debug(SPOTIFY_ENTITY_ID)
        # Try to select a device close to the original entity name; fallback to first real device.
        preferred_source = None
        if "spotify" not in str(original_eid).lower():
            preferred_source = str(original_eid).split(".", 1)[-1].replace("_", " ").strip()
        if not ensure_active_device(SPOTIFY_ENTITY_ID, prefer=preferred_source):
            print("No active Spotify device. Open Spotify on a device so it shows in source_list, then try again.")
            return

    # Map kind → HA media_content_type
    media_type = {
        "track": "music",
        "album": "album",
        "playlist": "playlist",
        "artist": "artist"
    }.get(kind, "music")

    # Resolve Spotify URI first (always)
    uri = search_spotify_uri(query, kind)
    if uri:
        query = uri

    print("We made it till here")
    print_spotify_debug(SPOTIFY_ENTITY_ID)

    # Send play; will retry once on 500 after ensuring device again
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


def get_spotify_state(entity_id: str) -> dict:
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.get(f"{BASE}/api/states/{entity_id}", headers=headers, timeout=8)
    r.raise_for_status()
    return r.json()


def print_spotify_debug(entity_id: str) -> None:
    try:
        st = get_spotify_state(entity_id)
        attrs = st.get("attributes", {})
        print("Spotify debug:",
              "state=", st.get("state"),
              "source=", attrs.get("source"),
              "sources=", attrs.get("source_list"))
    except Exception as e:
        print("Failed to read spotify state:", e)


def ensure_active_device(entity_id: str, *, prefer: str | None = None) -> bool:
    """
    Ensure a Spotify Connect device is selected.
    If 'prefer' is provided, select the closest matching device name first.
    Returns True if selected/ready; False otherwise.
    """
    st = get_spotify_state(entity_id)
    attrs = st.get("attributes", {})
    current = attrs.get("source")
    sources = attrs.get("source_list") or []

    if current:
        print("Spotify current source:", current)
        return True

    if not sources:
        print("Spotify source_list is EMPTY. Open Spotify on your phone/PC/TV so it appears.")
        return False

    # Filter out placeholders (e.g., "Home Assistant", "Default", "This phone")
    def is_placeholder(name: str) -> bool:
        n = (name or "").strip().lower()
        return n in {"home assistant", "default"} or "this phone" in n

    real_devices = [s for s in sources if not is_placeholder(s)]
    candidates = real_devices or sources

    # If we have a preferred name, choose the closest match (case-insensitive)
    choice = None
    if prefer:
        eid_name = str(prefer).strip().lower()
        # difflib expects a list of strings
        best = difflib.get_close_matches(eid_name, [c.lower() for c in candidates], n=1, cutoff=0.3)
        if best:
            # map back to the original-cased candidate
            idx = [c.lower() for c in candidates].index(best[0])
            choice = candidates[idx]
            print(f"Selecting closest Spotify device to '{prefer}': {choice}")

    if not choice:
        choice = candidates[0]
        print(f"No close match provided/found. Defaulting to: {choice}")

    select_source(entity_id, choice)

    # give HA a moment to reflect the change
    time.sleep(0.6)
    try:
        st2 = get_spotify_state(entity_id)
        ok = st2.get("attributes", {}).get("source") == choice
        print("Source select", "OK" if ok else "not reflected yet")
        return ok
    except Exception as e:
        print("Re-check after select failed:", e)
        return False


def get_source_list(entity_id: str) -> list[str]:
    headers = {"Authorization": f"Bearer {TOKEN}"}
    r = requests.get(f"{BASE}/api/states/{entity_id}", headers=headers, timeout=8)
    if r.status_code // 100 != 2:
        return []
    return r.json().get("attributes", {}).get("source_list", []) or []


def _ensure_uri(s: str) -> str | None:
    # Return spotify: URI if string already is a Spotify link.
    s = (s or "").strip()
    if s.startswith("spotify:"):
        return s
    m = re.match(r"https?://open\.spotify\.com/([a-z]+)/([A-Za-z0-9]+)", s) #Chatgpt was used to compute the REGEX
    if m:
        kind, sid = m.group(1), m.group(2)
        return f"spotify:{kind}:{sid}"
    return None


def search_spotify_uri(query: str, kind: str = "track") -> str | None:
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

    # Try to separate title and artist for better accuracy (for tracks/albums)
    parts = re.split(r"\bby\b", query, flags=re.IGNORECASE)
    if len(parts) >= 2 and kind in {"track", "album"}:
        title, artist = parts[0].strip(), parts[1].strip()
        if kind == "track":
            q = f'track:"{title}" artist:"{artist}"'
        else:
            q = f'album:"{title}" artist:"{artist}"'
    else:
        q = query

    # First try the requested kind
    try:
        res = sp.search(q=q, type=kind, limit=1, market="MT")
        items = res.get(f"{kind}s", {}).get("items", [])
        if items:
            uri = items[0].get("uri")
            if uri:
                print(f"Found URI: {uri}")
                return uri
    except Exception as e:
        print(f"Search failed for type {kind}: {e}")

    # Fallback order to avoid empty results (keeps it simple)
    fallback_order = {
        "playlist": ["track", "album", "artist"],
        "album":    ["track", "artist", "playlist"],
        "artist":   ["track", "album", "playlist"],
        "track":    ["album", "playlist", "artist"],
    }.get(kind, ["track", "album", "playlist", "artist"])

    for k in fallback_order:
        try:
            res = sp.search(q=query, type=k, limit=1, market="MT")
            items = res.get(f"{k}s", {}).get("items", [])
            if items:
                uri = items[0].get("uri")
                if uri:
                    print(f"Found {k} URI: {uri}")
                    return uri
        except Exception as e:
            print(f"Search failed for type {k}: {e}")

    print("No URI found for:", query)
    return None


def play_media(entity_id: str, media_content_id: str, media_content_type: str, *, kind: str = "track") -> None:
    """Send play_media command to Home Assistant (with preflight + single retry on 500)."""
    url = f"{BASE}/api/services/media_player/play_media"
    headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
    body = {
        "entity_id": entity_id,
        "media_content_id": media_content_id,
        "media_content_type": media_content_type
    }

    # ensure a real output device is selected 
    try:
        st = get_spotify_state(entity_id)
        attrs = st.get("attributes", {})
        if not attrs.get("source"):
            print("No Spotify output device selected — selecting one…")
            if not ensure_active_device(entity_id):
                print("No available Spotify Connect device. Open Spotify on any device and try again.")
                # Let HA error propagate so caller sees consistent behavior
    except Exception as e:
        print("Preflight state check failed (continuing anyway):", e)

    # --- First attempt ---
    r = requests.post(url, headers=headers, json=body, timeout=10)
    if r.status_code // 100 == 2:
        return

    print("play_media FAILED")
    print("URL:", url)
    print("BODY:", body)
    print("STATUS:", r.status_code)
    print("RESP:", r.text)

    # --- If HA threw a 500, try once more after re-ensuring device ---
    if r.status_code == 500:
        print("Server returned 500. Re-checking/setting Spotify device and retrying once…")
        try:
            if ensure_active_device(entity_id):
                time.sleep(0.6)  # small grace period for HA to reflect state
                r2 = requests.post(url, headers=headers, json=body, timeout=10)
                if r2.status_code // 100 == 2:
                    print("Retry succeeded.")
                    return
                print("Retry FAILED")
                print("STATUS:", r2.status_code)
                print("RESP:", r2.text)
        except Exception as e:
            print("Retry path threw:", e)

    r.raise_for_status()
