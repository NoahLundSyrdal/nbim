2# LLM Prompts & Approach

This file documents the concise prompts used by the prototype, the rationale, and tips for safe, repeatable classification.

## System role (seed)
You are a reconciliation analyst. Classify a dividend break and propose the next action. Return ONLY compact JSON with keys: label, reason, action, confidence (0..1).
Allowed labels: ["ok","fx_mismatch","fx_inversion_suspected","tax_rate_mismatch","gross_amount_mismatch","net_amount_mismatch","missing_nbim","missing_cust","other"]. One sentence for reason and one for action. Valid JSON only.

## Example user prompt (prototype)
Data is passed as a small JSON object containing only the most relevant fields.

{
  "NBIM": {"event_key": "...", "isin": "...", "gross": 1234.56, "net": 1000.00, "tax_rate": 0.15, "fx": 1.234},
  "CUST": {"event_key": "...", "isin": "...", "gross": 1234.56, "net": 1000.00, "tax_rate": 0.20, "fx": 1.234},
  "Flags": {"break_tax": true, "break_fx": false, "break_gross": false, "break_net": false, "diffs": {"gross":0.0, "net":0.0, "tax_rate":-0.05, "fx":0.0}}
}

Task: Classify the reconciliation break using one label from the allowed list, give a one-line reason, suggest a one-line remediation action, and provide a confidence between 0 and 1. Respond with JSON only.

## Prompting tips
- Keep the input minimal. Pass only the few fields needed for classification to reduce token usage and exposure of sensitive data.
- Use a deterministic/system instruction (temperature=0.0) for consistent outputs.
- Enforce JSON output and add a small post-processing step that extracts JSON when the model adds stray tokens.
- Cache model outputs during development to avoid repeated calls and cost.

## Fallback & safety
- The prototype can include a deterministic local fallback classifier (used when the LLM is unreachable) that maps rule-based flags to labels and suggested actions. This keeps the pipeline runnable offline and avoids blocking on model availability.
- For production, require human approval for any automated remediation with financial exposure above a configurable threshold.

## Why structured JSON
Structured JSON makes outputs machine-readable, reduces hallucination risk (model constrained to keys), and eases auditing and downstream automation.
