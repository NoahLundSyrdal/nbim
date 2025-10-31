## FX Correction Decisions

**IMMEDIATE CORRECTION: Samsung Electronics Co Ltd - 960789012**  
- **Market FX Evidence:** 0.007243 vs NBIM implied ~0.008234 vs Custody 1307.25 (inversion evident)  
- **Determination:** NBIM FX rate is incorrect due to inversion; Custody rate is clearly erroneous (1307.25) and not aligned with market  
- **Action:** Adjust NBIM side to use market FX rate of 0.007243 to correct valuation and recover $450,050 cash impact  
- **Deadline:** Immediate (24 hours)

**IMMEDIATE CORRECTION: Nestle SA - 970456789 (bank account 823456791)**  
- **Market FX Evidence:** 12.5693 vs NBIM 12.4567 vs Custody 1.0 (assumed custody base)  
- **Determination:** Market FX (12.5693) is more accurate than NBIM (12.4567)  
- **Action:** Adjust NBIM FX rate to 12.5693 to correct $6,200 cash impact  
- **Deadline:** Immediate (24 hours)

**IMMEDIATE CORRECTION: Apple Inc - 950123456**  
- **Market FX Evidence:** 10.4266 vs NBIM 11.2345 vs Custody 1.0  
- **Determination:** Market FX (10.4266) is correct; NBIM FX (11.2345) is overstated  
- **Action:** Adjust NBIM FX rate to 10.4266 to align valuation  
- **Deadline:** Within 48 hours (LOW priority, no cash impact)

**IMMEDIATE CORRECTION: Nestle SA - 970456789 (bank accounts 823456789 & 823456790)**  
- **Market FX Evidence:** 12.5693 vs NBIM 12.4567 vs Custody 1.0  
- **Determination:** Market FX (12.5693) is correct; NBIM FX (12.4567) is slightly off  
- **Action:** Adjust NBIM FX rate to 12.5693 for both accounts to ensure consistency  
- **Deadline:** Within 48 hours (LOW priority, no cash impact)

**SYSTEMIC FIX: Nestle SA & Samsung Electronics Co Ltd - Pattern Detected**  
- **Issue:** Repeated FX discrepancies with NBIM rates consistently differing from market rates; inversion and rate mapping errors observed (e.g., Samsung’s custody FX rate of 1307.25 vs market 0.007243)  
- **Root Cause:** FX rate inversion errors and outdated or incorrect FX rate mapping in NBIM data pipeline  
- **Action:** Update and validate FX rate mapping logic; implement automated reconciliation checks against market FX rates before settlement  
- **Owner:** FX Data Management Team & Reconciliation Systems Team

## Cash Impact Resolution
- **Total Exposure:** $456,250.00  
- **Primary Issue:** Samsung Electronics Co Ltd event 960789012 with $450,050 cash impact due to FX inversion and tax rate differences  
- **Resolution Path:**  
  1. Correct NBIM FX rate to market rate immediately to recover $450,050  
  2. Investigate and adjust tax rate discrepancies in coordination with tax compliance team  
  3. Correct Nestle SA FX rate on account 823456791 to recover $6,200  
  4. Monitor and validate all FX rates daily against market benchmarks to prevent recurrence

## Next Settlement Cycle Protection
1. **Implement automated FX rate validation against live market feeds prior to settlement**  
2. **Establish escalation protocol for any FX discrepancies exceeding predefined thresholds (e.g., >0.5%)**