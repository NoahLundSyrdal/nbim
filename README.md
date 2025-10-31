# nbim — LLM-powered Dividend Reconciliation (Pre-case)

A focused pre-case project exploring how LLMs and agent-based automation can accelerate
and improve dividend reconciliation between NBIM internal bookings and global custodian
reports. This repository contains the brief, datasets and guidance for a compact
prototype and an architecture vision.


┌──────────────┐          ┌──────────────────────────────┐          ┌────────────────┐
│  Agent 1     │          │          Agent 2             │          │    Agent 3     │
│  FX Diff     │  ─────▶  │  All Diffs + Summary + Rank │  ─────▶  │  Email Composer│
│ (Determine   │          │  (determine all differences, │          │  (make concise │
│  FX diffs)   │          │   summarize, rank by impact) │          │   email)       │
└─────┬────────┘          └───────────────┬──────────────┘          └──────┬─────────┘
      │                                   │                                │
      │ enriched breaks w/ FX deltas      │ prioritized summary + actions  │ email draft
      │                                   │                                │
      ▼                                   ▼                                ▼
  input breaks  ───────────────────────────────────────────────────────────▶ out/recon_email_draft.md


3. Analysis & Recommendations

This system demonstrates how agent-based automation can streamline financial reconciliation by combining data validation, LLM reasoning, and concise communication. The core opportunities lie in extending the existing agents for greater intelligence and transparency: automatic FX and dividend reconciliation with natural-language explanations, intelligent email drafts with embedded evidence, continuous FX exposure monitoring, anomaly clustering for break-pattern detection, and a natural-language query interface for ad-hoc reporting. Each enhancement focuses on reducing manual effort, improving interpretability, and ensuring audit-ready outputs.

Key risks include data quality issues, LLM hallucinations, privacy exposure, and operational reliability. These are mitigated through schema validation, strict JSON output formats, human-in-the-loop review, masking sensitive data, and versioned run metadata. Quick wins include adding input validation and immutable run snapshots; medium-term priorities are anomaly detection, structured prompt templates, and monitoring; and long-term goals are full audit reproducibility and regulated data governance. Success is measured by lower manual triage time, fewer false positives, and complete run traceability.