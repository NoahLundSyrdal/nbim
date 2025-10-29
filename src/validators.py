ALLOWED = {
  "ok","fx_mismatch","fx_inversion_suspected",
  "tax_rate_mismatch","gross_amount_mismatch","net_amount_mismatch",
  "missing_nbim","missing_cust","other"
}

def normalize_llm(obj: dict) -> dict:
    label = obj.get("label","other")
    if label not in ALLOWED:
        label = "other"
    reason = (obj.get("reason") or "").strip()
    action = (obj.get("action") or "").strip()
    try:
        conf = float(obj.get("confidence", 0.5))
    except Exception:
        conf = 0.5
    conf = max(0.0, min(1.0, conf))
    return {"label": label, "reason": reason, "action": action, "confidence": conf}