from llm_client import call_llm
import pandas as pd

def generate_business_summary(df: pd.DataFrame) -> str:
    """LLM synthesizes analysis with ACTUAL FX corrections"""
    
    # Prepare summary with FX analysis results
    summary_data = []
    for _, row in df.iterrows():
        item = {
            'event': row.get('event_key', 'Unknown'),
            'security': row.get('organisation', row.get('instrument_description', 'Unknown')),
            'break_type': row.get('break_label', 'Unknown'),
            'priority': row.get('priority', 'MEDIUM'),
            'cash_impact': row.get('cash_impact', 0),
            'bank_account': row.get('bank_account', 'Unknown'),
            # Include the actual FX analysis results
            'correct_side': row.get('correct_side', 'unknown'),
            'market_fx': row.get('market_fx'),
            'suggested_rate': row.get('suggested_rate'),
            'is_inversion': row.get('is_inversion', False)
        }
        
        summary_data.append(item)
    
    prompt = f"""
    As a senior reconciliation analyst, provide decisive actions based on ACTUAL FX analysis:

    {summary_data}

    Structure your response EXACTLY like this:

    ## FX Correction Decisions

    **🚨 IMMEDIATE CORRECTION: [Security] - [Event]**
    - **Market FX Evidence:** [market rate] vs [NBIM rate] vs [Custody rate]
    - **Determination:** [NBIM/Custody] has correct FX based on market data
    - **Action:** Adjust [incorrect side] to use [suggested rate]
    - **Deadline:** Immediate (24 hours)

    **⚠️ SYSTEMIC FIX: [Security] - Pattern Detected**
    - **Issue:** [Description of systematic error]
    - **Root Cause:** [Inversion error / Rate mapping bug / etc.]
    - **Action:** [Fix data pipeline / Update rate mapping / etc.]
    - **Owner:** [Team responsible]

    ## Cash Impact Resolution
    - **Total Exposure:** $[sum of all cash impacts]
    - **Primary Issue:** [Largest cash impact break]
    - **Resolution Path:** [Specific steps to recover funds]

    ## Next Settlement Cycle Protection
    1. **[Preventive measure 1]**
    2. **[Preventive measure 2]**

    Rules:
    - MAKE DECISIONS based on the FX analysis provided
    - Specify EXACT RATES to use for corrections
    - Assign ACTUAL OWNERS for each fix
    - Focus on RECOVERING CASH, not just describing problems
    """

    return call_llm(prompt)