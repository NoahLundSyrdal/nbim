# Dividend Reconciliation — Summary

## Break distribution
- **fx_mismatch**: 4
- **net_amount_mismatch**: 1

## Top items (P1/P2)

|   event_key | isin         |   bank_account | break_label                                               | llm_label           | llm_reason                                                                | llm_action                                                 | priority   | next_action_code   |
|------------:|:-------------|---------------:|:----------------------------------------------------------|:--------------------|:--------------------------------------------------------------------------|:-----------------------------------------------------------|:-----------|:-------------------|
|   960789012 | KR7005930003 |      712345678 | tax_rate_mismatch | fx_mismatch | net_amount_mismatch     | net_amount_mismatch | Net amounts differ by 450,050 due to tax rate and FX mismatch.            | Investigate tax rate and FX conversion discrepancies.      | P1         | AMT_N_005          |
|   950123456 | US0378331005 |      501234567 | fx_mismatch                                               | fx_mismatch         | Cust and NBIM have different FX rates, indicating a reconciliation break. | Investigate FX rate discrepancy and verify source data.    | P3         | FX_MIS_002         |
|   970456789 | CH0038863350 |      823456789 | fx_mismatch                                               | fx_mismatch         | FX rate discrepancy detected between NBIM and Cust.                       | Investigate FX rate difference and reconcile with source.  | P3         | FX_MIS_002         |
|   970456789 | CH0038863350 |      823456790 | fx_mismatch                                               | fx_mismatch         | FX rate discrepancy detected between NBIM and Cust.                       | Investigate FX conversion discrepancy and reconcile rates. | P3         | FX_MIS_002         |
|   970456789 | CH0038863350 |      823456791 | fx_mismatch | gross_amount_mismatch | net_amount_mismatch | fx_mismatch         | FX rate discrepancy detected between NBIM and Cust.                       | Investigate FX conversion factor alignment.                | P3         | FX_MIS_002         |