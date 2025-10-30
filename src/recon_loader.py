import pandas as pd
from pathlib import Path


def load_nbim_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';')
    df = df.rename(columns={
        'COAC_EVENT_KEY': 'event_key',
        'ISIN': 'isin',
        'ORGANISATION_NAME': 'organisation',
        'BANK_ACCOUNT': 'bank_account',             # keep per-leg key
        'GROSS_AMOUNT_QUOTATION': 'gross_nbim',
        'NET_AMOUNT_QUOTATION': 'net_nbim',
        'WTHTAX_RATE': 'tax_rate_nbim',
        'AVG_FX_RATE_QUOTATION_TO_PORTFOLIO': 'fx_nbim',
        'QUOTATION_CURRENCY': 'quotation_currency',
        'SETTLEMENT_CURRENCY': 'settlement_currency'
    })
    # keep currency columns too so we can detect cross-currency cases later
    df = df[['event_key','isin','organisation','bank_account',
             'gross_nbim','net_nbim','tax_rate_nbim','fx_nbim',
             'quotation_currency','settlement_currency']]
    df[['gross_nbim','net_nbim','tax_rate_nbim','fx_nbim']] = (
        df[['gross_nbim','net_nbim','tax_rate_nbim','fx_nbim']].apply(pd.to_numeric, errors='coerce')
    )
    # normalize bank_account to string (avoid 823456789 vs "823456789" mismatches)
    df['bank_account'] = df['bank_account'].astype(str).str.strip()
    df['isin'] = df['isin'].astype(str).str.upper().str.strip()
    df['event_key'] = df['event_key'].astype(str).str.strip()
    # normalize currency columns to upper-case 3-letter codes when present
    if 'quotation_currency' in df.columns:
        df['quotation_currency'] = df['quotation_currency'].astype(str).str.upper().str.strip()
    if 'settlement_currency' in df.columns:
        df['settlement_currency'] = df['settlement_currency'].astype(str).str.upper().str.strip()
    return df

def load_custody_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, sep=';')
    df = df.rename(columns={
        'COAC_EVENT_KEY': 'event_key',
        'ISIN': 'isin',
        # some feeds use BANK_ACCOUNTS (plural) — normalize to bank_account
        'BANK_ACCOUNTS': 'bank_account',
        'BANK_ACCOUNT': 'bank_account',
        'GROSS_AMOUNT': 'gross_cust',
        'NET_AMOUNT_QC': 'net_cust',
        'TAX_RATE': 'tax_rate_cust',
        'FX_RATE': 'fx_cust',
        'CURRENCIES': 'quotation_currency',
        'SETTLED_CURRENCY': 'settlement_currency'
    })
    # keep per-leg key
    required = ['event_key','isin','bank_account','gross_cust','net_cust','tax_rate_cust','fx_cust']
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Custody CSV missing columns needed for per-leg match: {missing}")

    df = df[required]
    df[['gross_cust','net_cust','tax_rate_cust','fx_cust']] = (
        df[['gross_cust','net_cust','tax_rate_cust','fx_cust']].apply(pd.to_numeric, errors='coerce')
    )
    df['bank_account'] = df['bank_account'].astype(str).str.strip()
    df['isin'] = df['isin'].astype(str).str.upper().str.strip()
    df['event_key'] = df['event_key'].astype(str).str.strip()
    # normalize currency columns to upper-case 3-letter codes when present
    if 'quotation_currency' in df.columns:
        df['quotation_currency'] = df['quotation_currency'].astype(str).str.upper().str.strip()
    if 'settlement_currency' in df.columns:
        df['settlement_currency'] = df['settlement_currency'].astype(str).str.upper().str.strip()
    return df

def load_and_align(nbim_path: str, custody_path: str) -> pd.DataFrame:
    nbim = load_nbim_csv(nbim_path)
    custody = load_custody_csv(custody_path)

    # 1-to-1 per-leg match
    merged = nbim.merge(
        custody,
        on=['event_key','isin','bank_account'],
        how='inner',
        suffixes=('_nbim','_cust')
    )

    # quick diffs
    for a, b in [
        ('gross_nbim','gross_cust'),
        ('net_nbim','net_cust'),
        ('tax_rate_nbim','tax_rate_cust'),
        ('fx_nbim','fx_cust'),
    ]:
        if a in merged.columns and b in merged.columns:
            merged[f'{a}_minus_{b}'] = merged[a] - merged[b]

    return merged

if __name__ == "__main__":
    # Resolve data files relative to the project root 
    data_dir = Path(__file__).resolve().parent.parent / "data"

    nbim_path = data_dir / "NBIM_Dividend_Bookings 1 (2).csv"
    custody_path = data_dir / "CUSTODY_Dividend_Bookings 1 (2).csv"

    merged_df = load_and_align(str(nbim_path), str(custody_path))
    print(merged_df)
