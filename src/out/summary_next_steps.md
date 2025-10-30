## Apple Inc (US0378331005) — Event 950123456
Market FX (Norges Bank): 10.426600 — nbim correct.

**Summary for ISIN: US0378331005 | Event Key: 950123456**

- **Type of Break**: FX Mismatch — NBIM and Custody are using different FX rates (NBIM: 11.2345, Cust: 10.4266), leading to a discrepancy in net value after FX conversion.
- **FX Correct Side**: NBIM (higher FX rate used; 11.2345) — NBIM’s FX rate is higher, suggesting it may be the correct or authoritative source, depending on business rules or reconciliation policy.
- **Who Should Act**: Both NBIM and Custody — since the discrepancy involves both systems, joint investigation and data validation are required.
- **Next Steps**:
  1. **
  2. **Check Cross-Currency Reversal Flag** — Ensure no cross-currency reversal or re-pricing logic is misapplied.
  3. **Reprice if Stale** — If the FX rate is outdated, recompute the value using the current or authoritative rate.
- **Resolution Criteria**:
  - Both systems must align FX rates (preferably use the same source or authoritative rate).
  - Reconciliation must reflect the same net value after FX adjustment.
  - Confirm that no re-pricing or reversal logic is misapplied.
  - Final resolution requires both systems to agree on the FX rate and net value, with a confidence level ≥ 0.85.


## Samsung Electronics Co Ltd (KR7005930003) — Event 960789012
Market FX (Norges Bank): 0.724300 — nbim correct.

**Summary for ISIN: KR7005930003 | Event: 960789012**

- **Type of Breaks**:  
  - Tax Rate Mismatch (NBIM tax rate 22% vs. Custody 20%)  
  - FX Mismatch (NBIM FX 0.008234 vs. Custody FX 0.7243 — likely misapplied or inverted)  
  - Net Amount Mismatch (NBIM net 6,769,950 vs. Custody net 7,220,000 — difference of 450,050)  

- **FX Correct Side**:  
  **NBIM** — FX rate 0.008234 is correctly applied (consistent with gross-to-net conversion), while Custody’s FX 0.7243 appears inverted or misapplied. **NBIM is the correct FX side** for this transaction.

- **Who Should Act**:  
  **Both NBIM and Custody** — since the discrepancy involves both tax rate and FX handling, and the error likely stems from reconciliation logic or data entry. Custody must verify FX rate application, while NBIM must validate tax rate and ensure FX is correctly applied to net.

- **Next Steps & Resolution Criteria**:  
  1. **Verify and correct tax rate application** — Confirm if 22% vs. 20% is a misalignment in tax rate mapping or if one side is applying a wrong rate.  
  2. **Reconcile FX rate** — Confirm if 0.008234 is the correct FX rate for this transaction (likely 1/122.000, not 0.7243). If 0.7243 is a misapplied inverse, correct it to 0.008234.  
  3. **Recompute net amount** — Recompute net from gross - tax - fees, ensuring ADR fee and restitution lines are correctly applied on both sides.  
  **Resolution Criteria**:  
  - All tax rates and FX rates must align with the correct conversion logic (NBIM FX 0.008234 is correct).  
  - Net amounts must match after recalculating with correct tax and FX adjustments.  
  - Both parties must validate and correct their internal mappings to ensure 100% reconciliation.

**Priority**: P1 — Critical discrepancy affecting net amount and tax/FX integrity.


## Nestle SA (CH0038863350) — Event 970456789
Market FX (Norges Bank): 1256.930000 — nbim correct.

**Summary for ISIN: CH0038863350 | Event Key: 970456789**

**Breaks Detected:**
- **FX Mismatch** (2 records): NBIM and Custody FX rates differ (12.4567 vs 11.4567), indicating potential misalignment in FX conversion factor or source.
- **Gross Amount Mismatch** (1 record): NBIM gross = 62,000 vs Custody gross = 62,000 → *no mismatch*.
- **Net Amount Mismatch** (1 record): NBIM net = 40,300 vs Custody net = 40,300 → *no mismatch*.
- **Gross Amount Mismatch** (1 record): NBIM gross = 31,000 vs Custody gross = 37,200 → **-6,200 difference**.
- **Net Amount Mismatch** (1 record): NBIM net = 20,150 vs Custody net = 24,180 → **-4,030 difference**.

**FX Correct Side:**
- **NBIM** (for FX mismatch records) — NBIM FX rate is higher than Custody, suggesting NBIM may be using a stale or incorrect rate.

**Who Should Act:**
- **Both NBIM and Custody** — since the discrepancy spans both systems, and the issue involves FX rate alignment and potential re-pricing.

**Next Steps & Resolution Criteria:**

1. **Investigate FX Rate Sources & Timestamps** — Verify that both systems are using the same FX rate source (e.g., Bloomberg, Reuters) and that timestamps align. Check if rates are stale or misaligned.

2. **Check Cross-Currency Reversal Flag** — Ensure that any cross-currency reversal (e.g., CHF to EUR) is correctly applied and that no manual adjustments or misapplications have occurred.

3. **Reprice if Stale** — If the FX rate is outdated, reprice the transaction using the current market rate to reconcile the difference. Confirm that the discrepancy is due to rate staleness, not a system error.

**Resolution Criteria:**
- All gross and net amounts must match across NBIM and Custody.
- FX rates must be identical (or within acceptable tolerance) across both systems.
- Reconciliation must be completed within 24 hours of detection.
- If discrepancy persists after re-pricing, escalate to system audit or FX rate validation team.

**Priority:** P3 — Requires attention but not urgent; resolve before end of day if possible.
