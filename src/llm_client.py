import json
from openai import OpenAI

# Local server + dummy key. Ready for openai swithch
CLIENT = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

MODEL = "qwen/qwen3-vl-4b"  

SYSTEM_INSTRUCTIONS = (
    "You are a reconciliation analyst. Classify a dividend break and propose the next action. "
    "Return ONLY compact JSON with keys: label, reason, action, confidence (0..1). "
    'Allowed labels: ["ok","fx_mismatch","fx_inversion_suspected","tax_rate_mismatch",'
    '"gross_amount_mismatch","net_amount_mismatch","missing_nbim","missing_cust","other"]. '
    "One sentence for reason and one for action. Valid JSON only."
)

def prompt(nbim: dict, cust: dict, flags: dict) -> str:
    return (
        f"{SYSTEM_INSTRUCTIONS}\n\n"
        f"Data:\nNBIM: {json.dumps(nbim, ensure_ascii=False)}\n"
        f"Cust: {json.dumps(cust, ensure_ascii=False)}\n"
        f"Flags: {json.dumps(flags, ensure_ascii=False)}\n"
        f"Rules:\n- Respond with JSON only.\n"
    )

def classify_locally(nbim: dict, cust: dict, flags: dict) -> dict:
    msg = prompt(nbim, cust, flags)
    resp = CLIENT.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": msg}],
        temperature=0.0,
        seed=42,
    )
    text = resp.choices[0].message.content.strip()

    # Harden: extract JSON if the model adds stray tokens
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]
    try:
        obj = json.loads(text)
    except Exception:
        obj = {"label":"other","reason":"invalid_json","action":"fallback_rule","confidence":0.2}
    # Minimal schema defaults
    obj.setdefault("label","other")
    obj.setdefault("reason","")
    obj.setdefault("action","")
    obj.setdefault("confidence",0.5)
    return obj
