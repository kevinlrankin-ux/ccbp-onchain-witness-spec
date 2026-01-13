# CCBP On-Chain Witness + Sandbox Intelligence Stack (v0.1)

This repository captures a **DB-minimizing, community-aware, non-weaponizable intelligence framework** built around:

- One-way integrity (CCBP-aligned)
- Edge-first querying (“ask the environment”)
- Minimal persistence by design
- Context-Aware Decision Memory (CDM)
- Community stewardship (energy caps + local offsets)

---

## What makes this different

Most systems:
- centralize data
- over-store telemetry
- lose decision context
- drift toward extractive intelligence

This stack:
- treats databases as **optional memory**
- keeps truth at the edge
- records *decisions*, not just data
- enforces non-authoritative boundaries
- preserves community capacity

---

## Key components

### 1) On-Chain Witness (WIT)
- Non-transferable, non-speculative provenance anchors
- Proves *existence and integrity* without disclosure

### 2) Utility/Access Token (UTL)
- Optional, transferable
- Gates access to **delayed, aggregated, non-actionable** C1 insights only

### 3) Sandbox Partitioning
- Entity → Project → Modality enclaves
- Default-deny cross-project sharing
- Single CTL export boundary

### 4) Edge-Query + Context Broker
- Ask devices/state directly
- Store rollups, exceptions, audits only
- Expand without DB schema churn

### 5) Context-Aware Decision Memory (CDM)
- Append-only decision ledger
- Outcome linking + supersession
- No PII, no signals, no surveillance

### 6) Community Stewardship Addendum
- Sandbox energy caps (non-authoritative)
- Local offsets (WBL, schools, infrastructure)
- Advisory-only “Intelligent Tax” assist

---

## Quick start

Run all conformance checks:
```bash
make test
```

Validate a folder of CDM records:
```bash
python conformance/cdm_ledger_validator.py cdm_records_sample
```

---

## Design commitments (locked)

- No raw proprietary data on-chain
- No tradable intelligence signals
- No external authority posture
- No urgency pressure
- Expansion without forced data hoarding

---

## Status

This repo is intentionally **spec-first**.
Implementation modules (chains, IoT stacks, AI runtimes) should live in separate repos once requirements stabilize.

---

*Capability can grow. Authority does not leak.*


## Publication & License

**Final Recommendation (locked):**
- Yes — publish on GitHub.
- Yes — under Apache 2.0.
- Yes — with explicit scope boundaries.

This repository defines the **playing field**.
It does not give away implementation advantage.

See:
- `LICENSE` (Apache 2.0)
- `USE_AND_INTENT.md`
