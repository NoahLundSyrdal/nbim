import re
import pandas as pd
from llm_client import call_llm
from pathlib import Path

def summarize_next_steps(df: pd.DataFrame) -> str:
    if df.empty:
        return "No breaks to summarize."

    results = []
    header = """You are a reconciliation analyst. 
Write one clear summary per group (ISIN + event_key).
Include:
- Type of break(s)
- FX correct side if present
- Who should act (NBIM/Custody/Both)
- 2–3 next steps and resolution criteria.
"""

    # Group by both event_key and isin so each Nestlé leg is merged once
    for (event, isin), group in df.groupby(["event_key", "isin"], dropna=False):
        org = group["organisation"].iloc[0]
        block = group.to_markdown(index=False)
        prompt = f"{header}\nSecurity: {org} ({isin}) | Event: {event}\nDetails:\n{block}\n\nWrite summary:"

        # call chat function here
        summary_text = call_llm(prompt)

        # If market_fx is present on the record, prefer a one-line market summary
        fx_one_liner = ""
        # use the first row as a representative record
        r = group.iloc[0]
        if "market_fx" in group.columns and not pd.isna(r.get("market_fx")):
            # 🧠 Fix inconsistent correctness labeling: trust whichever side is closer to market_fx
            try:
                if (
                    abs(r.get("fx_cust", 0) - r.get("market_fx", 0))
                    < abs(r.get("fx_nbim", 0) - r.get("market_fx", 0))
                ):
                    r["fx_correct_side"] = "custody"
                else:
                    r["fx_correct_side"] = "nbim"
            except Exception:
                # fall back to whatever the record contains
                pass

            # determine correct side robustly
            correct_side = r.get("fx_correct_side", "unknown") or "unknown"
            try:
                market_line = f"Market FX (Norges Bank): {float(r['market_fx']):.6f} — {correct_side} correct.\n\n"
                fx_one_liner = market_line
            except Exception:
                fx_one_liner = ""

        # If the LLM already included a 'verify fx source' instruction but we have
        # a market_fx available, remove that redundant bullet to avoid contradiction.
        try:
            if "verify fx source" in (summary_text or "").lower() and "market_fx" in group.columns and not group["market_fx"].isna().all():
                summary_text = re.sub(r"(?i)verify fx source[^.]*[.]", "", summary_text)
        except Exception:
            # be permissive — if regex fails, keep the original summary_text
            pass

        results.append(f"## {org} ({isin}) — Event {event}\n{fx_one_liner}{summary_text.strip()}\n")

    return "\n\n".join(results)


if __name__ == "__main__":
    df = pd.read_csv("out/recon_llm.csv")
    out = summarize_next_steps(df)
    Path("out/summary_next_steps.md").write_text(out, encoding="utf-8")
    print("✅ wrote out/summary_next_steps.md with", len(df.groupby(['event_key','isin'])), "sections")