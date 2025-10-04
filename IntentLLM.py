# IntentLLM.py
import json
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig

from states import states
from services import services

MODEL_ID = "google/gemma-2-9b-it"

USE_GPU = torch.cuda.is_available()
DEVICE = "cuda" if USE_GPU else "cpu"
print(f"Loading {MODEL_ID} on {DEVICE} (4-bit)…")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto",
    torch_dtype=torch.float16 if USE_GPU else torch.float32,
    low_cpu_mem_usage=True,
    quantization_config=bnb_config
).eval()
print("Model loaded.")

# ---------------------------
# Robust JSON extraction
# ---------------------------
def _extract_first_json(s: str) -> str | None:
    """Return first top-level {...} JSON object substring, or None."""
    i = s.find("{")
    if i == -1:
        return None
    depth, in_str, esc = 0, False, False
    for j in range(i, len(s)):
        ch = s[j]
        if in_str:
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': in_str = False
        else:
            if ch == '"': in_str = True
            elif ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    frag = s[i:j+1].strip()
                    frag = re.sub(r",(\s*[}\]])", r"\1", frag)  # trailing commas
                    return frag
    return None

def _first_entity_id(parsed: dict) -> str | None:
    """Try to find an entity_id in services (any shape) or devices."""
    svcs = parsed.get("services")

    # Case A: dict with "domain.action" key
    if isinstance(svcs, dict) and svcs:
        k0 = next(iter(svcs))
        if "." in k0:
            ent = svcs[k0].get("entity_id") if isinstance(svcs[k0], dict) else None
            if ent:
                return ent
        else:
            # Case C: {"media_player": {"turn_on": "media_player.turn_on"}} (no entity here)
            pass

    # Case B: list of dicts
    if isinstance(svcs, list) and svcs:
        ent = svcs[0].get("entity_id")
        if ent:
            return ent

    # Fallback: devices (dict with keys as entity_ids OR list of dicts)
    devs = parsed.get("devices")
    if isinstance(devs, dict) and devs:
        k0 = next(iter(devs))
        if isinstance(k0, str) and "." in k0:
            return k0
        v0 = devs[k0]
        if isinstance(v0, dict):
            ent = v0.get("entity_id")
            if ent:
                return ent
    if isinstance(devs, list) and devs:
        v0 = devs[0]
        if isinstance(v0, dict):
            ent = v0.get("entity_id")
            if ent:
                return ent
    return None

def _extract_action_domain(parsed: dict) -> tuple[str | None, str | None]:
    """Return (action, domain) from 'services' supporting three shapes."""
    svcs = parsed.get("services")

    # Case A: {"services": {"media_player.turn_on": {"entity_id":"..."}}}
    if isinstance(svcs, dict) and svcs:
        k0 = next(iter(svcs))
        if "." in k0:
            dom, act = k0.split(".", 1)
            return act, dom

        # Case C: {"services": {"media_player": {"turn_on": "media_player.turn_on", ...}}}
        inner = svcs[k0]
        if isinstance(inner, dict) and inner:
            act0 = next(iter(inner))           # e.g., "turn_on"
            return act0, k0                    # domain = outer key

    # Case B: {"services": [{"name":"turn_on","domain":"media_player", ...}]}
    if isinstance(svcs, list) and svcs:
        item = svcs[0]
        act = item.get("name") or item.get("action")
        dom = item.get("domain")
        return act, dom

    return None, None

# ---------------------------
# Main inference
# ---------------------------
def gemma(command: str):
    try:
        devicesJSON = states(timeout=8)
    except Exception as e:
        devicesJSON = {"error": f"states() failed: {e}"}
    try:
        servicesList = services(timeout=8)
    except Exception as e:
        servicesList = {"error": f"services() failed: {e}"}

    user_msg = (
        "You are an AI that controls a smart home. Map user commands to Home Assistant device settings.\n"
        "Return ONLY ONE JSON object. No markdown, no code fences, no extra text.\n\n"
        f"User command: {command}\n"
        f"Devices: {devicesJSON}\n\n"
        f"Services: {servicesList}\n\n"
        "If relevant devices exist, respond exactly as:\n"
        '{ "status": "success", "devices": { ... } | [ ... ], "services": { "<domain>.<action>": {"entity_id": "<eid>"} } }\n'
        "If Spotify or playing music or song or even AND ESPECIALLY IF the word play is mentioned, respond exactly as:\n"
        '{\n'
        '  "status": "success",\n'
        '  "devices": [ { "entity_id": "media_player.spotify", "name": "Spotify" } ],\n'
        '  "services": [ {\n'
        '     "name": "play_media",\n'
        '     "domain": "media_player",\n'
        '     "entity_id": "media_player.spotify",\n'
        '     "query": "<song, album, or playlist name from user command>",\n'
        '     "kind": "track | album | playlist",\n'
        '     "source": "<output device name if mentioned (e.g. Living Room TV)>"\n'
        '  } ]\n'
    '}\n\n'
        "Alternatively allowed (but please include entity_id if possible):\n"
        '{ "status":"success", "devices":[...], "services":[{"name":"turn_on","domain":"media_player","entity_id":"<eid>"}] }\n'
        "Otherwise respond:\n"
        '{ "status": "failure", "explanation": { ... } }'
    )

    prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": user_msg}],
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(prompt, return_tensors="pt")
    if USE_GPU:
        inputs = {k: v.to("cuda") for k, v in inputs.items()}

    out = model.generate(
        **inputs,
        max_new_tokens=512,
        do_sample=False,
        temperature=0.0,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=getattr(tokenizer, "pad_token_id", tokenizer.eos_token_id),
    )
    text = tokenizer.decode(out[0], skip_special_tokens=True)

    assistant_out = text.split(user_msg)[-1].strip() if user_msg in text else text.strip()
    json_str = _extract_first_json(assistant_out)
    if not json_str:
        raise ValueError(f"Model did not return a JSON object. Got:\n{assistant_out}")

    parsed = json.loads(json_str)

    if parsed.get("status") != "success":
        return None, None, None

    action, domain = _extract_action_domain(parsed)
    eid = _first_entity_id(parsed)

    if not action:
        raise ValueError(f"Could not determine action from 'services': {parsed.get('services')}")
    if not eid:
        raise ValueError(f"Could not determine entity_id from reply: {parsed}")
    if not domain:
        domain = eid.split(".", 1)[0]

    print("Parsed reply:", parsed)
    print("action:", action)
    print("domain:", domain)
    print("entity_id:", eid)

    return eid, domain, action, parsed
# ---------------------------
# Quick manual test
# ---------------------------
if __name__ == "__main__":
    print(gemma("turn on living room tv"))
