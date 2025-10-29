# nbim — LLM-powered Dividend Reconciliation (Pre-case)

A focused pre-case project exploring how LLMs and agent-based automation can accelerate
and improve dividend reconciliation between NBIM internal bookings and global custodian
reports. This repository contains the brief, datasets and guidance for a compact
prototype and an architecture vision.

## Background
NBIM processes ~8,000 dividend events annually across 9,000+ equity holdings. Daily
reconciliation between NBIM's internal booking system and the global custodian is
manual, time-consuming and error-prone. This pre-case explores how LLMs can help
detect, classify and—where safe—automate remediation for reconciliation breaks.

## Challenge
Design and implement an LLM-powered system to reconcile the provided dividend data
and demonstrate an approach for classifying and prioritizing breaks, recommending
remediations, and proposing an agent-based architecture that could operate safely in
production.

## Data provided
The dataset files included in this repository:
- `data/NBIM_Dividend_Bookings.csv` — NBIM internal booking records
- `data/CUSTODY_Dividend_Bookings.csv` — Global custodian records

Notes:
- The dataset contains three representative dividend events (distinct `coac_event_key`
	values) with varying complexity. Use these as test cases for classification and
	reconciliation logic.

## Technical constraints
- Budget: $15 USD for LLM API usage (OpenAI or Anthropic). Keep calls concise and
	batch where possible.
- Models: Any tier is allowed — prioritize architecture and agent design over model
	output polish.

## Required deliverables (what this README maps to)
1) Working prototype
	 - LLM integration that processes the test data (local demo).
	 - Classification & reconciliation logic (code + simple rules fallback).
	 - Documentation of prompts and approach (see "Prompts & approach").

2) Architecture vision
	 - Agent-based system design describing roles, communications, and safeguards.

3) Analysis & recommendations
	 - Innovative LLM use cases, risk assessment, and mitigation strategies.

## Prototype notes — minimum viable scope
Deliver a small local prototype that:
- Loads the two CSVs and aligns records by key fields (e.g., ISIN, pay date,
	gross/net amounts, `coac_event_key`).
- Runs reconciliation matching rules (exact matches, tolerant numeric/rounding
	checks, date tolerances) and produces a set of "breaks".
- Sends a concise summary of each break to an LLM to classify the break (e.g., data
	mismatch, timing difference, corporate action mapping, missing booking) and propose
	next steps (explainable, confidence score, suggested remediation or rule).
- Outputs a human-readable report (CSV or JSON) with classification, priority, and
	suggested remediation text.

Success criteria:
- Prototype can process the three test events and produce consistent classifications
	and actionable suggestions for at least the representative cases.

## Prompts & approach (documentation for prompt design)
Prompting strategy
- Keep prompts short and structured. Pass only the necessary fields for the break
	(e.g., ISIN, NBIM_amount, Custody_amount, NBIM_date, Custody_date, coac_event_key,
	any flags from rule-based checks).
- Ask the model for a classification label, a short rationale (1–2 sentences), a
	priority (High/Medium/Low), and a suggested remediation action.

Example structured prompt (pseudo-format):
"""
You are a financial reconciliation assistant.
Input: {json object with fields}
Task: Classify the reconciliation break, give a one-line reason, assign priority
(High/Medium/Low), and suggest a short remediation action (<=20 words).
Respond in JSON with keys: label, reason, priority, remediation, confidence (0-1).
"""

Prompting tips to stay within budget:
- Use small models for classification where possible and reserve larger or chain-of-
	thought calls for complex cases only.
- Cache model outputs for identical inputs during development to avoid repeated
	calls.

## Architecture vision — agent-based design
High-level components:
- Ingest agent: Normalizes and validates incoming files (CSV → canonical rows).
- Rule-based matcher: Fast deterministic matching for high-confidence pairs.
- LLM classifier agent: Receives unresolved breaks and returns classification,
	rationale, and remediation suggestions.
- Orchestrator agent: Applies policies, prioritizes remediations, triggers human
	review or automated remediations where allowed.
- Audit & safety layer: Maintains immutable logs, approval workflows and human-in-
	the-loop gates for sensitive actions.

Design notes:
- Use the LLM for interpretation, classification, and suggested fixes; keep final
	authority inside orchestrator or human reviewer depending on risk policies.
- Favor stateless, idempotent agents that communicate via well-defined message
	schemas (JSON) and store all decisions with a timestamp and model metadata.

## Analysis & recommendations
Innovative use cases
- Intelligent prioritization: LLMs can triage breaks by potential financial impact
	and remediation complexity, focusing humans on high-value items.
- Root-cause summarization: Aggregate similar breaks and let an LLM produce a
	concise root-cause hypothesis for batch remediation.
- Auto-generated remediation scripts: For low-risk, repetitive fixes, generate
	deterministic remediation actions (e.g., create booking correction template) and
	surface them for quick human approval.

Risk assessment & mitigations
- Risk: LLM hallucination proposing incorrect fixes.
	Mitigation: Require structured JSON outputs, confidence scores, and human approval
	for financial actions above thresholds. Keep rule-based guardrails.
- Risk: Data leakage to LLM provider.
	Mitigation: Minimize PII sent; anonymize fields where possible; use providers with
	enterprise contracts or deploy models in a VPC if required.
- Risk: Cost overruns.
	Mitigation: Rate-limit model calls, batch inputs, and cache responses.

## Presentation tips (8-minute demo)
Keep the demo compact:
1. 30s: One-line problem statement and approach.
2. 90s: Show data sample and how the prototype ingests it.
3. 2–3 minutes: Live demo — run the prototype on the three test events and show
	 the generated break classifications and suggested remediations.
4. 90s: Architecture vision (single slide) describing agents and safety layers.
5. 60s: Key benefits, risks, and recommended next steps.

Demo notes:
- Prepare cached model outputs in case of API latency or budget constraints.
- Have a short pre-recorded screencast ready as a backup.

## Next steps and suggested artifacts to add
- Prototype code: small Python script or notebook that loads CSVs, applies rules,
	and calls an LLM for unresolved breaks.
- prompts.md: store canonical prompt templates and iterations.
- tests/: unit tests for matching logic and at least two golden-case tests.
- `requirements.txt` or `pyproject.toml` with minimal dependencies (pandas, openai
	client or chosen SDK).

## How to run (suggested local flow)
1. Create a Python virtual environment and install dependencies.
2. Place CSVs in `data/` (already provided).
3. Run the prototype script to produce `output/reconciliation_report.json`.

Example commands (local developer):
```bash
# macOS / zsh
python -m venv .venv
source .venv/bin/activate
pip install pandas openai  # adjust for chosen provider
python scripts/run_reconciliation.py  # script to implement
```

## Licensing
See `LICENSE` in the repository root.

## Closing summary
This README provides a structured plan to build an LLM-enabled dividend
reconciliation prototype, a clear set of deliverables, prompt guidance, and an
agent-based architecture with safety controls. Next step: add the prototype code,
prompts file, and a small test harness for the three target `coac_event_key`
cases.

---
Generated and organized from the provided pre-case brief.