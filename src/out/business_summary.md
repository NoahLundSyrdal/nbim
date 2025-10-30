## FX Correction Decisions

**IMMEDIATE CORRECTION: Apple Inc - 950123456**
- **Market FX Evidence:** 10.4266 vs 11.2345 (NBIM) vs 1.0 (Custody)
- **Determination:** NBIM has correct FX based on market data
- **Action:** Adjust Custody to use 10.4266
- **Deadline:** Immediate (24 hours)
- **Owner:** FX Reconciliation Team - Custody Systems

**IMMEDIATE CORRECTION: Nestle SA - 970456789 (Event 823456790)**
- **Market FX Evidence:** 12.5693 vs 12.4567 (NBIM) vs 1.0 (Custody)
- **Determination:** NBIM has correct FX based on market data
- **Action:** Adjust Custody to use 12.5693
- **Deadline:** Immediate (24 hours)
- **Owner:** FX Reconciliation Team - Custody Systems

**IMMEDIATE CORRECTION: Samsung Electronics Co Ltd - 960789012**
- **Market FX Evidence:** 0.007243 vs 0.008234 (NBIM) vs 1307.25 (Custody)
- **Determination:** NBIM has correct FX based on market data
- **Action:** Adjust Custody to use 0.007243
- **Deadline:** Immediate (24 hours)
- **Owner:** FX Reconciliation Team - Custody Systems

**SYSTEMIC FIX: Nestle SA - Pattern Detected**
- **Issue:** Multiple events for same security (970456789) show identical break type and market FX, but different bank accounts and net diffs — indicates rate mapping bug
- **Root Cause:** Rate mapping engine fails to distinguish between custodial and non-custodial accounts, leading to double-counting of FX differences
- **Action:** Fix data pipeline to enforce unique rate mapping per bank account, validate against market FX before reconciliation
- **Owner:** Data Engineering Team - FX Reconciliation Pipeline

## Cash Impact Resolution
- **Total Exposure:** $450,050.00
- **Primary Issue:** Samsung Electronics Co Ltd - 960789012 (net_diff: -450050)
- **Resolution Path:** 
  1. Execute immediate correction to Custody using 0.007243
  2. Reconcile 450,050 USD to NBIM side
  3. Initiate recovery of funds via bank account 712345678
  4. Confirm settlement with custodian bank within 24 hours

## Next Settlement Cycle Protection
1. **Implement real-time FX validation layer** — enforce market rate comparison before finalizing any FX reconciliation entry
2. **Deploy automated rate mapping override** — if market FX differs from NBIM by >0.0001, auto-flag for manual override with audit trail

**Note:** All corrections must be executed within 24 hours to prevent further exposure. Immediate action required to recover $450,050 from Samsung.