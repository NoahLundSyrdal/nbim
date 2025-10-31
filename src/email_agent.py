# src/email_agent.py
from __future__ import annotations

import pandas as pd
from typing import List, Dict, Any
from llm_client import call_llm


def _rows_to_summary_items(df: pd.DataFrame) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []
    for _, row in df.iterrows():
        items.append({
            "event": row.get("event_key", "Unknown"),
            "security": row.get("organisation", row.get("instrument_description", "Unknown")),
            "break_type": row.get("break_label", "Unknown"),
            "priority": row.get("priority", "MEDIUM"),
            "cash_impact": row.get("cash_impact", 0),
            "bank_account": row.get("bank_account", "Unknown"),
            "correct_side": row.get("correct_side", "unknown"),
            "market_fx": row.get("market_fx"),
            "suggested_rate": row.get("suggested_rate"),
            "is_inversion": row.get("is_inversion", False),
            "nbim_fx": row.get("nbim_fx"),
            "custody_fx": row.get("custody_fx"),
        })
    return items


def generate_recon_email_concise(
    df_with_fx: pd.DataFrame,
    business_summary_md: str,
    *,
    audience: str = "FX Reconciliation Team",
    sender_name: str = "Noah",
) -> str:
    """
    LLM CALL #3 (concise): feed the full business summary + raw items and have the LLM
    SELECT the most important points. Output is intentionally short.
    """
    items = _rows_to_summary_items(df_with_fx)

    prompt = f"""
You are a senior reconciliation analyst. You will receive a full summary and structured
per-break facts. Write an extremely concise, send-ready email that surfaces ONLY what matters.

**STRICT FORMAT (Markdown only, no extra commentary):**
Subject: Reconciliation — Top FX Corrections (24h)
To: {audience}
Cc:
---
Executive (≤2 sentences).

**Immediate Corrections (max 3)**
- [Security] — [Event]: Fix [side] → [rate]. Impact: $[amount].

**Systemic Fixes (max 2, optional)**
- [pattern/owner/action]

**Cash Impact**
- Total exposure: $[sum]
- Largest driver: [Security/Event] $[amount]

**Next Cycle**
- [Preventive step 1]
- [Preventive step 2]

Best,
{sender_name}

**DECISION RULES (very important):**
- Choose items by: highest cash_impact, then priority (HIGH>MEDIUM>LOW), then is_inversion=True.
- Prefer FX-related breaks; ignore non-FX noise unless they dominate exposure.
- Use exact rates from the data; do NOT invent numbers.
- Keep the total email body under ~120 words. No filler.

=== FULL BUSINESS SUMMARY (Markdown) ===
{business_summary_md}

=== STRUCTURED FACTS (JSON-like) ===
{items}
"""
    return call_llm(prompt)


def save_email_draft(email_md: str, out_path: str) -> None:
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(email_md)
