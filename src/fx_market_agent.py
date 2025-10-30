import pandas as pd
from llm_client import call_llm
import json
import requests
from time import sleep
from typing import Optional

def fetch_market_fx(base: str, quote: str, date: str) -> Optional[float]:
    """Fetch daily spot FX rate from Norges Bank Open Data API"""
    url = (
        f"https://data.norges-bank.no/api/data/EXR/B.{base}.{quote}.SP"
        f"?startPeriod={date}&endPeriod={date}&format=sdmx-json"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Drill into the dynamic series keys
        series = data["data"]["dataSets"][0]["series"]
        key = next(iter(series))                 # get first key dynamically
        obs = series[key]["observations"]
        first_obs = list(obs.values())[0]        # first observation
        value = float(first_obs[0])              # numeric value
        return value
    except Exception as e:
        print(f"Could not fetch {base}/{quote} FX for {date}: {e}")
        return None

def get_base_currency_from_isin(isin: str) -> str:
    """Determine base currency from ISIN prefix"""
    if not isin or pd.isna(isin):
        return "USD"
    
    prefix = str(isin)[:2].upper()
    currency_map = {
        "US": "USD", "KR": "KRW", "CH": "CHF", "GB": "GBP", 
        "SE": "SEK", "JP": "JPY", "NO": "NOK", "CA": "CAD", 
        "EU": "EUR", "DE": "EUR", "FR": "EUR", "IT": "EUR"
    }
    return currency_map.get(prefix, "USD")

def analyze_fx_discrepancy(nbim_fx: float, cust_fx: float, market_fx: float, 
                          base_ccy: str, quote_ccy: str, security: str) -> dict:
    """LLM analyzes FX rates and makes CORRECTIONS decisions"""
    
    # Calculate actual business impact
    nbim_error_pct = abs((nbim_fx - market_fx) / market_fx * 100) if market_fx else 100
    cust_error_pct = abs((cust_fx - market_fx) / market_fx * 100) if market_fx else 100
    is_inversion = abs(nbim_fx * cust_fx - 1) < 0.01 if nbim_fx and cust_fx else False
    
    prompt = f"""
    As NBIM Treasury FX Analyst, make correction decisions for {security} ({base_ccy}/{quote_ccy}):

    MARKET DATA:
    - Norges Bank Rate: {market_fx}
    - NBIM Used: {nbim_fx} ({nbim_error_pct:.1f}% error)
    - Custody Used: {cust_fx} ({cust_error_pct:.1f}% error)
    - Inversion Error: {is_inversion}

    REQUIRED DECISIONS:
    1. Which system has the correct rate? (Answer: nbim/custody/both_wrong)
    2. What specific rate should we mandate for reconciliation?
    3. Is this a systematic error requiring process change?

    Return JSON with ACTIONS: 
    {{
        "correct_side": "nbim|custody|both_wrong",
        "mandated_rate": {market_fx},  // Always use market rate as truth
        "required_correction": "string describing specific fix",
        "process_improvement": "string for systematic fix",
        "confidence": 0.0-1.0
    }}
    """
    
    response = call_llm(prompt)
    try:
        return json.loads(response)
    except:
        return {
            "correct_side": "both_wrong", 
            "mandated_rate": market_fx,
            "required_correction": f"Use Norges Bank rate: {market_fx}",
            "process_improvement": "Validate all FX rates against central bank data",
            "confidence": 0.9
        }

def verify_fx_with_intelligence(df: pd.DataFrame) -> pd.DataFrame:
    """Apply LLM intelligence to FX breaks with actual market data"""
    
    result = df.copy()
    fx_analysis = []
    
    for _, row in df.iterrows():
        if row.get('break_fx'):
            # Get base currency from ISIN
            isin = row.get('isin')
            base_ccy = get_base_currency_from_isin(isin)
            quote_ccy = "NOK"  # NBIM's base currency
            
            # Get security name for context
            security = row.get('organisation') or row.get('instrument_description') or 'Unknown Security'
            
            # Try to get date for FX lookup
            fx_date = row.get('exdate') or row.get('payment_date') or "2025-04-25"
            
            # Fetch actual market FX rate from Norges Bank
            market_fx = fetch_market_fx(base_ccy, quote_ccy, fx_date)
            
            if market_fx:
                print(f"💰 Market FX for {base_ccy}/{quote_ccy} on {fx_date}: {market_fx}")
                
                # Analyze with LLM using actual market data - NOW INCLUDES SECURITY PARAMETER
                analysis = analyze_fx_discrepancy(
                    row.get('fx_nbim', 0), 
                    row.get('fx_cust', 0), 
                    market_fx,
                    base_ccy, 
                    quote_ccy,
                    security  # ← ADD THIS LINE
                )
                analysis['market_fx'] = market_fx
                fx_analysis.append(analysis)
            else:
                # No market data available
                fx_analysis.append({
                    "correct_side": "unknown", 
                    "is_inversion": False, 
                    "suggested_rate": None, 
                    "confidence": 0.0,
                    "reason": "No market FX data available",
                    "market_fx": None
                })
        else:
            # Not an FX break
            fx_analysis.append({})
    
    # Add analysis columns to DataFrame
    if fx_analysis:
        analysis_df = pd.DataFrame(fx_analysis)
        result = pd.concat([result, analysis_df], axis=1)
    
    return result