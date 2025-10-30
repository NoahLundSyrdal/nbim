import pandas as pd
from llm_client import call_llm
import json
import requests
from time import sleep
from typing import Optional

# Global cache to avoid redundant API calls
FX_CACHE = {}

def fetch_market_fx(base: str, quote: str, date: str) -> Optional[float]:
    """Fetch daily spot FX rate from Norges Bank with caching"""
    
    # Create cache key
    cache_key = f"{base}_{quote}_{date}"
    
    # Return cached result if available
    if cache_key in FX_CACHE:
        print(f"📦 Using cached FX: {base}/{quote} on {date} = {FX_CACHE[cache_key]}")
        return FX_CACHE[cache_key]
    
    # Otherwise fetch from API
    url = (
        f"https://data.norges-bank.no/api/data/EXR/B.{base}.{quote}.SP"
        f"?startPeriod={date}&endPeriod={date}&format=sdmx-json"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        series = data["data"]["dataSets"][0]["series"]
        key = next(iter(series))
        obs = series[key]["observations"]
        first_obs = list(obs.values())[0]
        value = float(first_obs[0])
        
        # Normalize per-100 currencies
        PER_100_CURRENCIES = {"JPY", "KRW", "HUF", "ISK", "CLP", "IDR", "CHF"}
        
        if base.upper() in PER_100_CURRENCIES:
            normalized_value = value / 100.0
            print(f"🔧 Normalized {base}/NOK from {value} (per 100) to {normalized_value} (per 1)")
            # Cache BEFORE printing "fetched" message
            FX_CACHE[cache_key] = normalized_value
            print(f"💰 Fetched FX: {base}/{quote} on {date} = {normalized_value}")  # Changed to "Fetched"
            return normalized_value
        
        # Cache BEFORE printing
        FX_CACHE[cache_key] = value
        print(f"💰 Fetched FX: {base}/{quote} on {date} = {value}")  # Changed to "Fetched"
        return value
        
    except Exception as e:
        print(f"❌ Could not fetch {base}/{quote} FX for {date}: {e}")
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
    """DETERMINISTIC analysis first, then LLM for explanation"""
    
    # Calculate actual errors (DETERMINISTIC - NO HALLUCINATION POSSIBLE)
    nbim_error_pct = abs((nbim_fx - market_fx) / market_fx * 100) if market_fx else 100
    cust_error_pct = abs((cust_fx - market_fx) / market_fx * 100) if market_fx else 100
    is_inversion = abs(nbim_fx * cust_fx - 1) < 0.01
    
    # DETERMINISTIC DECISION LOGIC (Pure Math)
    if cust_error_pct > 50 and nbim_error_pct < 10:
        correct_side = "nbim"
        wrong_side = "custody"
        error_description = f"Custody rate {cust_fx} is {cust_error_pct:.1f}% off market"
    elif nbim_error_pct > 50 and cust_error_pct < 10:
        correct_side = "custody"
        wrong_side = "nbim"
        error_description = f"NBIM rate {nbim_fx} is {nbim_error_pct:.1f}% off market"
    elif nbim_error_pct < cust_error_pct:
        correct_side = "nbim"
        wrong_side = "custody"
        error_description = f"NBIM closer to market (error: {nbim_error_pct:.1f}% vs {cust_error_pct:.1f}%)"
    else:
        correct_side = "custody"
        wrong_side = "nbim"
        error_description = f"Custody closer to market (error: {cust_error_pct:.1f}% vs {nbim_error_pct:.1f}%)"
    
    # Special case: FX = 1.0 means "no conversion" which is ALWAYS wrong for cross-currency
    if cust_fx == 1.0 and base_ccy != quote_ccy:
        correct_side = "nbim"
        wrong_side = "custody"
        error_description = f"Custody using 1.0 (no FX conversion) for {base_ccy}→{quote_ccy}"
    elif nbim_fx == 1.0 and base_ccy != quote_ccy:
        correct_side = "custody"
        wrong_side = "nbim"
        error_description = f"NBIM using 1.0 (no FX conversion) for {base_ccy}→{quote_ccy}"
    
    # NOW use LLM only for rich explanation and systematic pattern detection
    prompt = f"""
    As NBIM FX Analyst, explain this FX discrepancy for executive summary:

    DETERMINISTIC ANALYSIS (ALREADY DECIDED):
    - Security: {security} ({base_ccy}/{quote_ccy})
    - Market Rate (Norges Bank): {market_fx}
    - NBIM Used: {nbim_fx} (error: {nbim_error_pct:.1f}%)
    - Custody Used: {cust_fx} (error: {cust_error_pct:.1f}%)
    - **Decision: {correct_side.upper()} is CORRECT, {wrong_side.upper()} must adjust**
    - Reason: {error_description}

    YOUR TASK (explanation only - do NOT change the decision):
    1. Explain WHY this error likely occurred (stale rate? manual entry? system bug?)
    2. Is this a one-off error or systematic issue?
    3. Suggest process improvement to prevent recurrence

    Return JSON:
    {{
        "root_cause_hypothesis": "string (1 sentence)",
        "is_systematic": true/false,
        "process_improvement": "string (specific action)",
        "confidence": 0.0-1.0
    }}
    """
    
    response = call_llm(prompt)
    try:
        llm_insight = json.loads(response)
    except:
        llm_insight = {
            "root_cause_hypothesis": "Unable to determine root cause",
            "is_systematic": False,
            "process_improvement": "Manual review required",
            "confidence": 0.5
        }
    
    # Return deterministic decision + LLM enrichment
    return {
        "correct_side": correct_side,
        "mandated_rate": market_fx,
        "required_correction": f"Adjust {wrong_side} from {cust_fx if wrong_side == 'custody' else nbim_fx} to {market_fx}",
        "error_description": error_description,
        "nbim_error_pct": round(nbim_error_pct, 2),
        "cust_error_pct": round(cust_error_pct, 2),
        "is_inversion": is_inversion,
        # LLM-generated insights
        "root_cause_hypothesis": llm_insight.get("root_cause_hypothesis", "Unknown"),
        "is_systematic": llm_insight.get("is_systematic", False),
        "process_improvement": llm_insight.get("process_improvement", "Manual review"),
        "confidence": llm_insight.get("confidence", 0.7)
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