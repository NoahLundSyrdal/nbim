import requests
import pandas as pd
from time import sleep
from typing import Optional


def fetch_market_fx(base: str, quote: str, date: str) -> Optional[float]:
    """Fetch daily spot FX rate from Norges Bank Open Data API (SDMX-JSON format).
    Example endpoint:
      https://data.norges-bank.no/api/data/EXR/B.USD.NOK.SP?startPeriod=2025-04-25&endPeriod=2025-04-25&format=sdmx-json
    """
    url = (
        f"https://data.norges-bank.no/api/data/EXR/B.{base}.{quote}.SP"
        f"?startPeriod={date}&endPeriod={date}&format=sdmx-json"
    )
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        # Drill into the dynamic series keys (e.g. "0:0:0:USD:NOK")
        series = data["data"]["dataSets"][0]["series"]
        key = next(iter(series))                 # get first key dynamically
        obs = series[key]["observations"]
        first_obs = list(obs.values())[0]        # first observation
        value = float(first_obs[0])              # numeric value
        return value
    except Exception as e:
        print(f"Could not fetch {base}/{quote} FX for {date}: {e}")
        return None


def _coerce_date_value(val) -> str:
    """Coerce pandas/numpy/str date-like values to YYYY-MM-DD string."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return ""
    try:
        # pandas Timestamp or datetime-like
        if hasattr(val, "strftime"):
            return val.strftime("%Y-%m-%d")
        return str(val)
    except Exception:
        return str(val)


def _find_date_col(df: pd.DataFrame, preferred: Optional[str]) -> Optional[str]:
    """Return a date column name present in df. Try preferred first, then common names (case-insensitive)."""
    if preferred and preferred in df.columns:
        return preferred
    # case-insensitive search
    cols_map = {c.lower(): c for c in df.columns}
    candidates = ["dividend_date", "payment_date", "value_date", "ex_date", "record_date", "paymentdate", "value_date", "pay_date"]
    for c in candidates:
        if c in cols_map:
            return cols_map[c]
    # fallback: look for any column containing 'date'
    for k, orig in cols_map.items():
        if "date" in k:
            return orig
    return None


def verify_fx_against_market(df: pd.DataFrame, date_col: Optional[str] = "record_date") -> pd.DataFrame:
    """Compare NBIM & Custody FX to market rate; add fx_correct_side + market_fx columns.

    Enhancements:
    - Logs actions and decisions so it's visible when nothing was fetched.
    - Attempts to infer a date column if the requested one is missing.
    - Falls back to a default date (2025-04-25) when no date column is found.
    - Caches market FX per (base,quote,date) to avoid duplicate API calls.
    """
    print(f"verify_fx_against_market: called with date_col={date_col}")
    print(f"verify_fx_against_market: dataframe columns={list(df.columns)}; rows={len(df)}")

    chosen_date_col = _find_date_col(df, date_col)
    if chosen_date_col is None:
        print("verify_fx_against_market: no date column found; will use default date '2025-04-25' for all rows")
    else:
        if chosen_date_col != date_col:
            print(f"verify_fx_against_market: using inferred date column '{chosen_date_col}' instead of requested '{date_col}'")
        else:
            print(f"verify_fx_against_market: using date column '{chosen_date_col}'")

    DEFAULT_DATE = "2025-04-25"
    market_cache: dict = {}
    results = []
    for i, r in df.reset_index(drop=True).iterrows():
        # infer base currency from ISIN prefix when possible
        isin = None
        try:
            isin = r.get("isin") if "isin" in r.index else None
        except Exception:
            isin = None

        prefix = str(isin)[:2].upper() if isin else ""
        base_map = {
            "US": "USD",
            "KR": "KRW",
            "CH": "CHF",
            "GB": "GBP",
            "SE": "SEK",
            "JP": "JPY",
            "NO": "NOK",
            "CA": "CAD",
            "EU": "EUR",
        }
        base = base_map.get(prefix, "USD")
        quote = "NOK"

        # event identifier for better logs
        event_key = r.get("event_key") if "event_key" in r.index else None

        # pick date value
        if chosen_date_col:
            raw_date = r.get(chosen_date_col)
            date = _coerce_date_value(raw_date) or DEFAULT_DATE
        else:
            date = DEFAULT_DATE

        cache_key = (base, quote, date)
        if cache_key in market_cache:
            market_fx = market_cache[cache_key]
            print(f"[cache] date={date} ISIN={isin} event_key={event_key} -> market_fx={market_fx}")
        else:
            print(f"Fetching FX for {base}/{quote} on {date} (ISIN={isin} event_key={event_key})")
            market_fx = fetch_market_fx(base, quote, date)
            market_cache[cache_key] = market_fx

            # Cross-rate fallback: if direct pair missing, try base->USD and USD->NOK to compute base/NOK
            if market_fx is None and base != "USD":
                print(f"Direct {base}/{quote} not available for {date}; attempting cross-rate via USD")
                usd_to_nok = market_cache.get(("USD", "NOK", date)) or fetch_market_fx("USD", "NOK", date)
                if usd_to_nok:
                    market_cache[("USD", "NOK", date)] = usd_to_nok
                base_to_usd = market_cache.get((base, "USD", date)) or fetch_market_fx(base, "USD", date)
                if base_to_usd:
                    market_cache[(base, "USD", date)] = base_to_usd

                if usd_to_nok and base_to_usd:
                    try:
                        market_fx = usd_to_nok / base_to_usd
                        market_cache[cache_key] = market_fx
                        print(f"💱 Cross-rate {base}/{quote} ≈ {market_fx:.6f} (computed from {base}/USD and USD/NOK)")
                    except Exception as e:
                        print(f"Failed to compute cross-rate for {base}/{quote} on {date}: {e}")

        if market_fx is None:
            print(f"No market FX available for {base}/{quote} on {date} (row {i} event_key={event_key}); marking fx_correct_side=unknown")
            results.append({"market_fx": None, "fx_correct_side": "unknown"})
            # polite to the API even when cached misses
            sleep(0.1)
            continue

        # handle potential missing fx values in rows
        nbim_fx = r.get("fx_nbim") if "fx_nbim" in r.index else None
        cust_fx = r.get("fx_cust") if "fx_cust" in r.index else None
        try:
            diff_nbim = abs((nbim_fx or 0) - market_fx)
            diff_cust = abs((cust_fx or 0) - market_fx)
        except Exception:
            diff_nbim = float("inf")
            diff_cust = float("inf")

        # prefer the side whose FX is closest to the market FX
        if diff_cust < diff_nbim:
            side = "custody"
        else:
            side = "nbim"

        print(f"Result row {i} event_key={event_key} ISIN={isin}: market_fx={market_fx} nbim={nbim_fx} cust={cust_fx} -> {side}")
        results.append({"market_fx": market_fx, "fx_correct_side": side})
        sleep(0.1)  # polite to the API

    df_out = pd.concat([df.reset_index(drop=True), pd.DataFrame(results)], axis=1)
    return df_out