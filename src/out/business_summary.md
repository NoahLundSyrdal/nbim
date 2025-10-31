## FX Correction Decisions

**IMMEDIATE CORRECTION: Samsung Electronics Co Ltd - 960789012**  
- **Market FX Evidence:** 0.007243 vs 0.008234 vs 1307.25  
- **Determination:** NBIM FX rate (0.008234) is incorrect; market FX (0.007243) is accurate and custody rate (1307.25) appears inverted or erroneous  
- **Action:** Adjust NBIM FX rate to market FX rate of 0.007243 to correct valuation and recover $450,050 cash impact  
- **Deadline:** Immediate (24 hours)

**IMMEDIATE CORRECTION: Nestle SA - 970456789 (Bank Account 823456791)**  
- **Market FX Evidence:** 12.5693 vs 12.4567 vs 1.0  
- **Determination:** Market FX (12.5693) is correct; NBIM FX (12.4567) is slightly off, custody rate (1.0) is incorrect  
- **Action:** Adjust NBIM FX rate to market FX rate of 12.5693 to recover $6,200 cash impact  
- **Deadline:** Immediate (24 hours)

**IMMEDIATE CORRECTION: Apple Inc - 950123456**  
- **Market FX Evidence:** 10.4266 vs 11.2345 vs 1.0  
- **Determination:** Market FX (10.4266) is correct; NBIM FX (11.2345) is overstated; custody rate (1.0) is incorrect  
- **Action:** Adjust NBIM FX rate to market FX rate of 10.4266  
- **Deadline:** Within 48 hours (LOW priority, no cash impact)

**IMMEDIATE CORRECTION: Nestle SA - 970456789 (Bank Accounts 823456789 & 823456790)**  
- **Market FX Evidence:** 12.5693 vs 12.4567 vs 1.0  
- **Determination:** Market FX (12.5693) is correct; NBIM FX (12.4567) is slightly off; custody rate (1.0) is incorrect  
- **Action:** Adjust NBIM FX rate to market FX rate of 12.5693  
- **Deadline:** Within 48 hours (LOW priority, no cash impact)

**SYSTEMIC FIX: Nestle SA & Apple Inc - Pattern Detected**  
- **Issue:** Consistent undervaluation of NBIM FX rates vs market FX rates and custody rates defaulting to 1.0, indicating incorrect custody FX application  
- **Root Cause:** Rate mapping bug causing custody FX rates to default to 1.0 and slight lag in NBIM FX rate updates  
- **Action:** Update FX rate mapping logic to pull accurate custody FX rates and synchronize NBIM FX rates with market FX daily  
- **Owner:** FX Data Management Team

**SYSTEMIC FIX: Samsung Electronics Co Ltd - Critical FX Inversion**  
- **Issue:** Extreme discrepancy in custody FX rate (1307.25) vs market and NBIM rates, indicating inversion or data entry error  
- **Root Cause:** FX inversion error in custody system or data feed  
- **Action:** Implement validation checks on FX rates to detect and block inversion errors before reconciliation  
- **Owner:** Custody Operations & Data Quality Team

## Cash Impact Resolution
- **Total Exposure:** $456,250.00  
- **Primary Issue:** Samsung Electronics Co Ltd event 960789012 with $450,050 cash impact due to FX and tax rate discrepancies  
- **Resolution Path:**  
  1. Correct NBIM FX rate to market FX rate immediately to reflect true valuation  
  2. Engage Custody Operations to verify and correct custody FX rate inversion  
  3. Recover $450,050 through adjustment entries and confirm with counterparties  
  4. For Nestle SA $6,200 cash impact, adjust NBIM FX rate and reconcile cash differences promptly

## Next Settlement Cycle Protection
1. **Implement automated FX rate validation and reconciliation alerts to detect large discrepancies pre-settlement**  
2. **Enhance coordination between FX Data Management, Custody Operations, and Reconciliation teams to ensure timely and accurate FX rate updates**