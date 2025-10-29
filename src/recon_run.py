import pandas as pd
from recon_loader import load_and_align  
from recon_breaks import classify_breaks
from llm_client import classify_locally
from validators import normalize_llm
from report import save_reports
from playbook import playbook, assign_priority

def to_nbim_dict(r):
    return {
        "event_key": r["event_key"],
        "isin": r.get("isin"),
        "bank_account": r.get("bank_account"),
        "gross": r.get("gross_nbim"),
        "net": r.get("net_nbim"),
        "tax_rate": r.get("tax_rate_nbim"),
        "fx": r.get("fx_nbim"),
    }

def to_cust_dict(r):
    return {
        "event_key": r["event_key"],
        "isin": r.get("isin"),
        "bank_account": r.get("bank_account"),
        "gross": r.get("gross_cust"),
        "net": r.get("net_cust"),
        "tax_rate": r.get("tax_rate_cust"),
        "fx": r.get("fx_cust"),
    }

def to_flags(r):
    return {
        "break_tax": bool(r.get("break_tax")),
        "break_fx": bool(r.get("break_fx")),
        "break_gross": bool(r.get("break_gross")),
        "break_net": bool(r.get("break_net")),
        "diffs": {
            "gross": float((r.get("gross_nbim") or 0) - (r.get("gross_cust") or 0)),
            "net": float((r.get("net_nbim") or 0) - (r.get("net_cust") or 0)),
            "tax_rate": float((r.get("tax_rate_nbim") or 0) - (r.get("tax_rate_cust") or 0)),
            "fx": float((r.get("fx_nbim") or 0) - (r.get("fx_cust") or 0)),
        }
    }

from pathlib import Path


if __name__ == "__main__":
    # Resolve data files relative to project root 
    data_dir = Path(__file__).resolve().parent.parent / "data"

    merged = load_and_align(
        str(data_dir / "NBIM_Dividend_Bookings 1 (2).csv"),
        str(data_dir / "CUSTODY_Dividend_Bookings 1 (2).csv"),
    )

    flagged = classify_breaks(merged)

    broken = flagged[flagged["break_label"] != "ok"].copy()
    results = []
    for _, row in broken.iterrows():
        nbim = to_nbim_dict(row)
        cust = to_cust_dict(row)
        flags = to_flags(row)
        llm = classify_locally(nbim, cust, flags)
        llm = normalize_llm(llm)
        results.append(llm)

    # attach LLM outputs
    broken = broken.reset_index(drop=True)
    if results:
        broken[["llm_label","llm_reason","llm_action","llm_confidence"]] = pd.DataFrame(
            [(r.get("label"), r.get("reason"), r.get("action"), r.get("confidence")) for r in results]
        )
        # Use the playbook for next_action_code/standard_step but compute
        # priority dynamically based on monetary impact and label.
        pb = broken.apply(lambda r: pd.Series(playbook(r.get("llm_label") or "other")), axis=1)
        # Attach the non-priority fields from the playbook
        broken[["next_action_code", "standard_step"]] = pb[["next_action_code", "standard_step"]]

        # Compute priority using assign_priority
        def _compute_priority(r):
            label = r.get("llm_label") or r.get("break_label") or "other"
            diffs = {
                "gross": float((r.get("gross_nbim") or 0) - (r.get("gross_cust") or 0)),
                "net": float((r.get("net_nbim") or 0) - (r.get("net_cust") or 0)),
            }
            return assign_priority(label, diffs)

        broken["priority"] = broken.apply(_compute_priority, axis=1)
    print("\n=== PER-LEG RECON (all rows) ===")
    print(flagged[["event_key","isin","bank_account","gross_nbim","gross_cust","net_nbim","net_cust","break_label"]])

    if not broken.empty:
        print("\n=== LLM SUGGESTIONS (only breaks) ===")
        print(broken[["event_key","isin","bank_account","break_label","llm_label","llm_reason","llm_action","llm_confidence"]])


    save_reports(flagged, broken)
    print("\nSaved: out/recon_flagged.csv, out/recon_llm.csv, out/summary.md")
