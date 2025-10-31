2# LLM Prompts & Approach
# LLM Prompts & Approach

This file documents the concise prompts used by the prototype, the rationale, and practical tips for safe, repeatable classification and decision gating when using LLMs in financial workflows.

## System role (seed)
You are a reconciliation analyst. Classify a dividend break and propose the next action. Return ONLY compact JSON with keys: label, reason, action, confidence (0..1).
Allowed labels: ["ok","fx_mismatch","fx_inversion_suspected","tax_rate_mismatch","gross_amount_mismatch","net_amount_mismatch","missing_nbim","missing_cust","other"]. One sentence for reason and one for action. Valid JSON only.

## Example user prompt (prototype)
Data is passed as a small JSON object containing only the most relevant fields.

```json
{
  "NBIM": {"event_key": "...", "isin": "...", "gross": 1234.56, "net": 1000.00, "tax_rate": 0.15, "fx": 1.234},
  "CUST": {"event_key": "...", "isin": "...", "gross": 1234.56, "net": 1000.00, "tax_rate": 0.20, "fx": 1.234},
  "Flags": {"break_tax": true, "break_fx": false, "break_gross": false, "break_net": false, "diffs": {"gross":0.0, "net":0.0, "tax_rate":-0.05, "fx":0.0}}
}
```

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

## Prompts & approach — safe autonomous operations

This project uses LLMs for reconciliation classification and for decision support in automated workflows. Below are compact, production-focused prompt templates, design rules, and post-processing guidance to keep outputs predictable, auditable, and safe for financial use.

### Design principles for prompts
- Minimal input: supply only fields required for the decision (reduces exposure and tokens).
- Deterministic behavior: use temperature=0 and explicit system instructions when the output must be machine-parsed.
- Constrain output shape: require strict JSON schema and validate it programmatically.
- Fail-fast and safe-defaults: if validation fails, fall back to rule-based actions or require human approval.
- Include provenance fields: source ids, timestamps, model_version in every prompt/response exchange.

### Core prompt templates (examples)

1) Classification (reconciliation breaks)

System: You are a reconciliation analyst. Classify the break using the allowed labels and return ONLY valid JSON.

User (input JSON):
```json
{
  "context": {"NBIM": {...}, "CUST": {...}},
  "flags": {...},
  "meta": {"request_id": "<uuid>", "timestamp": "<iso>", "model_version": "v1.2"}
}
```

Response schema (required):
```json
{
  "label": "one of [ok,fx_mismatch,...]",
  "reason": "one-sentence",
  "action": "one-sentence remediation",
  "confidence": 0.0
}
```

2) Pre-execution gate (before automated trade/payment)

System: You're a pre-execution risk gate. Evaluate whether the proposed action is within policy and safe to auto-execute. Return JSON with verdict, checks, and recommended action.

User (input JSON):
```json
{ "proposed_action": {...}, "current_positions": {...}, "limits": {...}, "meta": {...} }
```

Response schema:
```json
{
  "verdict": "approve|reject|require_manual",
  "failed_checks": ["limit_exceeded","liquidity_risk"],
  "rationale": "short text",
  "confidence": 0.0
}
```

3) Execution summary / human-readable audit

System: Summarize the executed action in plain language for an auditor (<=2 sentences), include request_id and model_version.

User: `{ "execution_record": {...}, "meta": {...} }`

Response: `{ "summary": "...", "request_id": "...", "model_version": "..." }`

### Prompt construction checklist
- Always include a system role that mandates JSON-only output and enumerates allowed keys.
- Include a small "meta" block with request_id, timestamp and model_version.
- Use examples in the system prompt to show expected values and edge cases.
- Provide deterministic constraints: "temperature=0", "max_tokens" tuned to output size, and explicit instruction to never invent numeric IDs or financial amounts.

### Post-processing & validation
- Parse the model output strictly as JSON; if parsing fails or keys are missing, treat it as a validation failure and trigger the fallback.
- Validate numeric ranges (e.g., confidence in [0,1], amounts non-negative, notional caps) before applying any automated action.
- Enforce schema using a JSON schema validator and reject responses that don't match exactly.
- Add server-side sanity checks: compare recommended action against hard limits and circuit-breaker state.

### Testing and QA for prompts
- Unit tests: verify prompt templates produce expected outputs against a mocked model (happy and edge cases).
- Regression/backtest: run the model on historical reconciliations and compare the label distribution vs known ground truth.
- Shadow-run: run the full decision pipeline in parallel to live (no execution) for a configurable period and measure false positives/negatives.
- Adversarial tests: inject malformed or adversarial inputs to validate fallback and safety behavior.

### Versioning, change control, and audit
- Embed `model_version` and `prompt_template_version` in every exchange and store them with the immutable audit record.
- Require code review and a short test-run (shadow-run) before changing any prompt that affects automated execution.
- Keep a changelog section at the bottom of this file for prompt and policy updates.

### Minimal safety policy for LLM-driven actions
1. Any automated action with financial exposure above the configured threshold must receive a pre-execution `verdict: approve` from the gate and have either (a) `verdict==approve` and `confidence >= threshold` or (b) explicit human approval.
2. If the model returns `require_manual` or the response fails validation, do not execute and escalate.
3. Maintain an immutable log of raw prompt, model response, parsed decision, and final action for at least the retention period required by compliance.

### Example quick templates (copyable)
- Classification system seed:
  "You are a reconciliation analyst. Given the input JSON, return ONLY valid JSON with keys: label, reason, action, confidence. Allowed labels: [ok,fx_mismatch,fx_inversion_suspected,tax_rate_mismatch,gross_amount_mismatch,net_amount_mismatch,missing_nbim,missing_cust,other]. Confidence must be a number between 0 and 1."

- Pre-execution gate seed:
  "You are a risk gate. Evaluate the proposed_action and respond with JSON: {verdict, failed_checks, rationale, confidence}. Verdict must be one of approve,reject,require_manual. Use policy in 'limits' to check exposures. Return JSON only."

### Change log
- 2025-10-30: Added 'Prompts & approach' section with safety templates, post-processing guidance, and policy snippets.
