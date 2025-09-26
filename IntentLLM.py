# IntentLLM.py
import os, json, torch
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from states import states  # make sure states() does the HTTP call *inside* the function with timeout

MODEL_ID = "google/gemma-2-9b-it"  # instruction-tuned
DEVICE = "cuda"

# --- Load once globally ---
print(f"Loading model on {DEVICE}...")

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,                  # set False for 8-bit
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",          # best quantization type
    bnb_4bit_compute_dtype=torch.float16
)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    device_map="auto",
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
    quantization_config=bnb_config
)
print("Model loaded ✅")

# --- Function just runs inference ---
def gemma(command: str) -> str:
    try:
        devicesJSON = states(timeout=8)
    except Exception as e:
        devicesJSON = {"error": f"states() failed: {e}"}

    user_msg = (
        "You are an AI that controls a smart home. Map user commands to Home Assistant device settings."
        """Matching rules (VERY IMPORTANT):
- Normalize text (lowercase, strip punctuation). Consider device name, area, type/class, and any aliases.
- Compute fuzzy similarity between the user command and each device’s composite string: "<area> <device name> <type> <aliases>".
- Confidence thresholds:
  - If top score ≥ 0 select that device."""
        "Return ONLY ONE JSON object with no extra text, no backticks, no explanations.\n\n"
        f"User command: {command}\n"
        f"Devices: {devicesJSON}\n\n"
        'If relevant devices exist, respond exactly as:\n'
        '{ "status": "success", "devices": { ... },}\n'
        "Otherwise respond:\n"
        '{ "status": "failure", "explanation": { ... } }'
    )
    print(user_msg)

    prompt = tokenizer.apply_chat_template(
        [{"role": "user", "content": user_msg}],
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(prompt, return_tensors="pt")
    if DEVICE == "cuda":
        inputs = {k: v.to(DEVICE) for k, v in inputs.items()}

    out = model.generate(
        **inputs,
        max_new_tokens=180,
        do_sample=False,
        temperature=0.0,
        eos_token_id=tokenizer.eos_token_id,
        pad_token_id=getattr(tokenizer, "pad_token_id", tokenizer.eos_token_id),
    )
    text = tokenizer.decode(out[0], skip_special_tokens=True)

    reply = text.split(user_msg)[-1].strip() if user_msg in text else text.strip()

    print(reply)
    
    data = json.loads(reply)
    entity_id = data["devices"][0]["entity_id"]
    print(entity_id)
    return reply
