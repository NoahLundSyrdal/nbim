## FX Correction Decisions

**🚨 IMMEDIATE CORRECTION: Apple Inc - 950123456**
- **Market FX Evidence:** 10.4266 vs 11.2345 (NBIM) vs 1.0 (Custody)
- **Determination:** NBIM has correct FX based on market data
- **Action:** Adjust Custody to use 10.4266
- **Deadline:** Immediate (24 hours)
- **Owner:** Custody Reconciliation Team

**🚨 IMMEDIATE CORRECTION: Nestle SA - 970456789 (Account 823456789)**
- **Market FX Evidence:** 1256.93 vs 12.4567 (NBIM) vs 1.0 (Custody)
- **Determination:** NBIM has correct FX based on market data
- **Action:** Adjust Custody to use 1256.93
- **Deadline:** Immediate (24 hours)
- **Owner:** Custody Reconciliation Team

**🚨 IMMEDIATE CORRECTION: Nestle SA - 970456789 (Account 823456790)**
- **Market FX Evidence:** 1256.93 vs 12.4567 (NBIM) vs 1.0 (Custody)
- **Determination:** NBIM has correct FX based on market data
- **Action:** Adjust Custody to use 1256.93
- **Deadline:** Immediate (24 hours)
- **Owner:** Custody Reconciliation Team

**⚠️ SYSTEMIC FIX: Nestle SA - Pattern Detected**
- **Issue:** Multiple identical events (970456789) with same break type but different cash impacts and accounts — indicates data duplication or misalignment
- **Root Cause:** Rate mapping bug causing duplicate entries with inconsistent FX rates
- **Action:** Fix data pipeline to deduplicate and enforce single FX rate per event/account combination
- **Owner:** Data Engineering & Validation Team

**⚠️ SYSTEMIC FIX: Samsung Electronics Co Ltd - 960789012**
- **Issue:** Critical cash impact of $450,050 due to tax + FX mismatch
- **Root Cause:** Inversion error in FX rate mapping — market rate 0.7243 vs reported 1307.25
- **Action:** Fix inversion error in FX rate mapping and update all related custodian records
- **Owner:** FX Rate Mapping & Inversion Validation Team

## Cash Impact Resolution
- **Total Exposure:** $450,050.00
- **Primary Issue:** Samsung Electronics Co Ltd — $450,050 cash impact due to inversion error
- **Resolution Path:**
  1. Reconcile all inversion errors in Samsung’s FX mapping
  2. Apply market rate 0.7243 to all affected accounts
  3. Initiate recovery of $450,050 via bank reconciliation and settlement adjustment
  4. Escalate to Risk & Compliance for audit trail and regulatory alignment

## Next Settlement Cycle Protection
1. **Implement real-time FX rate validation engine** — automatically flag inversion errors and mismatched rates before settlement
2. **Deploy rate mapping audit trail** — log all FX rate adjustments with timestamp, user, and reason for auditability and recovery

**Note:** All corrections must be completed within 24 hours. Immediate recovery of $450,050 is non-negotiable.