import numpy as np
import pandas as pd

def classify_breaks(df: pd.DataFrame) -> pd.DataFrame:
    """Pure deterministic break detection - no LLM"""
    out = df.copy()
    
    # Your existing comparison logic
    out["break_tax"] = ~np.isclose(out["tax_rate_nbim"], out["tax_rate_cust"], rtol=1e-4, atol=1e-2)
    out["break_fx"] = ~np.isclose(out["fx_nbim"], out["fx_cust"], rtol=1e-4, atol=1e-2)
    out["break_gross"] = ~np.isclose(out["gross_nbim"], out["gross_cust"], rtol=1e-4, atol=1e-2)
    out["break_net"] = ~np.isclose(out["net_nbim"], out["net_cust"], rtol=1e-4, atol=1e-2)
    
    # Enhanced break labeling
    def label_break(row):
        reasons = []
        if row["break_tax"]: 
            reasons.append(f"tax_rate_diff:{row['tax_rate_nbim']}vs{row['tax_rate_cust']}")
        if row["break_fx"]: 
            reasons.append(f"fx_diff:{row['fx_nbim']}vs{row['fx_cust']}")
        if row["break_gross"]: 
            reasons.append(f"gross_diff:{row['gross_nbim']-row['gross_cust']:.0f}")
        if row["break_net"]: 
            reasons.append(f"net_diff:{row['net_nbim']-row['net_cust']:.0f}")
            
        return " | ".join(reasons) if reasons else "ok"
    
    out["break_label"] = out.apply(label_break, axis=1)
    return out