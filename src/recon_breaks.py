import numpy as np
import pandas as pd

ABS = 1e-2
REL = 1e-4

def _close(a, b):
    if pd.isna(a) or pd.isna(b): return False
    return np.isclose(a, b, rtol=REL, atol=ABS)

def classify_breaks(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["break_tax"]   = ~(out.apply(lambda r: _close(r.get("tax_rate_nbim"), r.get("tax_rate_cust")), axis=1))
    out["break_fx"]    = ~(out.apply(lambda r: _close(r.get("fx_nbim"), r.get("fx_cust")), axis=1))
    out["break_gross"] = ~(out.apply(lambda r: _close(r.get("gross_nbim"), r.get("gross_cust")), axis=1))
    out["break_net"]   = ~(out.apply(lambda r: _close(r.get("net_nbim"),   r.get("net_cust")), axis=1))

    def label(r):
        reasons = []
        if r["break_tax"]: reasons.append("tax_rate_mismatch")
        if r["break_fx"]:
            # quick inversion hint
            if pd.notna(r.get("fx_nbim")) and pd.notna(r.get("fx_cust")):
                prod = r["fx_nbim"] * r["fx_cust"]
                if np.isfinite(prod) and np.isclose(prod, 1.0, rtol=1e-3, atol=1e-3):
                    reasons.append("fx_inversion_suspected")
                else:
                    reasons.append("fx_mismatch")
            else:
                reasons.append("fx_mismatch")
        if r["break_gross"]: reasons.append("gross_amount_mismatch")
        if r["break_net"]:   reasons.append("net_amount_mismatch")
        return "ok" if not reasons else " | ".join(reasons)

    out["break_label"] = out.apply(label, axis=1)
    return out
