import pandas as pd
from pathlib import Path

def save_reports(flagged: pd.DataFrame, broken: pd.DataFrame, outdir="out"):
    out = Path(outdir); out.mkdir(exist_ok=True)
    flagged.to_csv(out/"recon_flagged.csv", index=False)
    if not broken.empty:
        broken.to_csv(out/"recon_llm.csv", index=False)

    # Markdown summary 
    by_label = broken["llm_label"].value_counts().to_dict()
    lines = ["# Dividend Reconciliation — Summary",
             "",
             "## Break distribution",
             *(f"- **{k}**: {v}" for k,v in by_label.items()),
             "",
             "## Top items (P1/P2)",
             ""]
    cols = ["event_key","isin","bank_account","break_label",
            "llm_label","llm_reason","llm_action","priority","next_action_code"]
    top = broken.sort_values(["priority","llm_confidence"], ascending=[True,False])[cols].head(10)
    lines.append(top.to_markdown(index=False))
    (out/"summary.md").write_text("\n".join(lines), encoding="utf-8")
