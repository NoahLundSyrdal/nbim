def playbook(label: str) -> dict:
    table = {
        "fx_inversion_suspected": {
            "priority": "P1",
            "next_action_code": "FX_INV_001",
            "standard_step": "Recompute using 1/fx; verify currency direction (QC↔SC) and data source; request custodian correction if confirmed."
        },
        "fx_mismatch": {
            "priority": "P2",
            "next_action_code": "FX_MIS_002",
            "standard_step": "Compare NBIM vs custodian FX source & timestamp; check cross-currency reversal flag; reprice if stale."
        },
        "tax_rate_mismatch": {
            "priority": "P2",
            "next_action_code": "TAX_003",
            "standard_step": "Validate country treaty rate & relief-at-source vs reclaim; confirm ADR vs ORD; recalc expected tax."
        },
        "gross_amount_mismatch": {
            "priority": "P2",
            "next_action_code": "AMT_G_004",
            "standard_step": "Check nominal/position sizing, splits, rounding; confirm any fees deducted from gross."
        },
        "net_amount_mismatch": {
            "priority": "P2",
            "next_action_code": "AMT_N_005",
            "standard_step": "Recompute net from gross - tax - fees; verify ADR fee & restitution lines."
        },
        "missing_nbim": {
            "priority": "P1",
            "next_action_code": "MISS_N_006",
            "standard_step": "Create provisional NBIM booking; escalate for approval."
        },
        "missing_cust": {
            "priority": "P1",
            "next_action_code": "MISS_C_007",
            "standard_step": "Open ticket with custodian; attach NBIM event facts."
        },
        "ok": {
            "priority": "P3",
            "next_action_code": "OK_000",
            "standard_step": "No action."
        },
        "other": {
            "priority": "P3",
            "next_action_code": "OTHER_999",
            "standard_step": "Manual review."
        },
    }
    return table.get(label, table["other"])


def assign_priority(label: str, diffs: dict) -> str:
    """Assign a priority based on break label and numeric diffs.

    Rules implemented:
    - If label indicates a missing booking or fx inversion suspicion -> P1
    - If abs(net) or abs(gross) > 200_000 -> P1
    - If tax rate mismatch and net > 100_000 -> P1
    - If abs(net) or abs(gross) > 50_000 -> P2
    - Otherwise P3

    Args:
        label: the LLM/classification label (may contain multiple tokens)
        diffs: dict with numeric keys 'gross' and 'net' (numbers or numeric-strings)

    Returns:
        One of 'P1','P2','P3'
    """
    try:
        gross_diff = abs(float(diffs.get("gross", 0) or 0))
    except Exception:
        gross_diff = 0.0
    try:
        net_diff = abs(float(diffs.get("net", 0) or 0))
    except Exception:
        net_diff = 0.0

    # urgent labels
    if any(k in (label or "") for k in ["missing_nbim", "missing_cust", "fx_inversion_suspected"]):
        return "P1"

    # direct monetary thresholds
    if net_diff > 200_000 or gross_diff > 200_000:
        return "P1"

    # tax-related cases escalate earlier
    if "tax_rate_mismatch" in (label or "") and net_diff > 100_000:
        return "P1"

    if net_diff > 50_000 or gross_diff > 50_000:
        return "P2"

    return "P3"
