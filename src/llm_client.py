import json
import os
import warnings
from openai import OpenAI

# Configuration: prefer environment variables. This makes the repository
# usable with either a local LLM (LM Studio / llm server) or the OpenAI API.
#
# - If LLM_LOCAL_BASE_URL is set, it will be used as the client base URL.
# - Otherwise OPENAI_API_KEY (and optional OPENAI_API_BASE) will be used.
# - If none are set we fall back to the previous local default but emit a
#   warning so the user understands why a connection to localhost is attempted.

def _make_client():
    local_base = os.getenv("LLM_LOCAL_BASE_URL")
    local_key = os.getenv("LLM_LOCAL_API_KEY", "lm-studio")
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE")

    if local_base:
        return OpenAI(base_url=local_base, api_key=local_key)
    if api_key:
        # The OpenAI client constructor accepts api_key and optional base
        if api_base:
            return OpenAI(api_key=api_key, base_url=api_base)
        return OpenAI(api_key=api_key)

    warnings.warn(
        "No OPENAI_API_KEY or LLM_LOCAL_BASE_URL set; defaulting to http://127.0.0.1:1234/v1. "
        "If you want to use the OpenAI cloud API, set OPENAI_API_KEY in your environment.",
        UserWarning,
    )
    return OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")


CLIENT = _make_client()

MODEL = os.getenv("LLM_MODEL", "qwen/qwen3-vl-4b")

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
    """Return a minimal, robust classification dict.

    This function is defensive: if the configured LLM is unreachable it returns
    a sensible fallback instead of raising an exception that aborts the run.
    """
    msg = prompt(nbim, cust, flags)
    try:
        resp = CLIENT.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": msg}],
            temperature=0.0,
            seed=42,
        )
        text = resp.choices[0].message.content
        if text is None:
            raise RuntimeError("LLM returned empty response")
        text = text.strip()
    except Exception as e:
        # Return a conservative fallback classification so the recon run can continue.
        return {
            "label": "other",
            "reason": f"llm_unavailable: {str(e)}",
            "action": "fallback_rule",
            "confidence": 0.2,
        }

    # Harden: extract JSON if the model adds stray tokens
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start:end+1]
    try:
        obj = json.loads(text)
    except Exception:
        obj = {"label": "other", "reason": "invalid_json", "action": "fallback_rule", "confidence": 0.2}
    # Minimal schema defaults
    obj.setdefault("label", "other")
    obj.setdefault("reason", "")
    obj.setdefault("action", "")
    obj.setdefault("confidence", 0.5)
    return obj


def call_llm(prompt_text: str) -> str:
    """Send a free-text prompt to the configured LLM and return the raw text reply.

    This helper is useful for summary/insight prompts that don't fit the
    structured classify_locally(nbim,cust,flags) signature.
    """
    try:
        resp = CLIENT.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt_text}],
            temperature=0.0,
        )
        text = resp.choices[0].message.content
        if text is None:
            return ""
        return text.strip()
    except Exception as e:
        # Safe fallback when local LLM or API is unreachable
        return f"[LLM unavailable — fallback] {str(e)}"
