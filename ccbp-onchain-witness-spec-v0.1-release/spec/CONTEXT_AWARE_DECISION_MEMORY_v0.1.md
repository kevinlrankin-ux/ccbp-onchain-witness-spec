# Context-Aware Decision Memory (CDM) (v0.1)
*(Decision Trace + Constraint Context + Outcome Links — Low-DB, High-Lift)*

**Status:** Draft  
**Purpose:** Provide a lightweight, append-only “memory of judgment” that enables human + AI teams to learn over time **without** storing excessive raw data or creating surveillance posture.

> **Core idea:** Store *decisions and their context*, not everything that happened.

---

## 1) What CDM is (and is not)

### CDM is
- a **decision ledger** (append-only)
- scoped to an **Entity** and **Project Partition**
- includes **constraints-in-force** (scope, energy cap, export class)
- links to **state snapshots by reference** (not raw payloads)
- optionally links to **outcomes** later (what changed, what worked)

### CDM is not
- a full telemetry database
- a user surveillance system
- a taskmaster or external authority
- a trading signal engine

---

## 2) CDM record types (v0.1)

### 2.1 DecisionRecord (required)
Captures a discrete decision made by a human, an AI-assisted workflow, or both.

### 2.2 OutcomeRecord (optional)
Adds follow-up: what happened after the decision, with evidence references.

### 2.3 AssumptionRecord (optional)
Stores explicit assumptions that shaped the decision (helps learning).

### 2.4 ConstraintRecord (optional)
Registers changes in constraints/policies (energy cap, scope bindings).

---

## 3) Minimal DecisionRecord fields (normative)

```json
{
  "cdm_v": "0.1",
  "record_type": "decision",
  "record_id": "uuid",
  "time_utc": "RFC3339",
  "entity": {
    "entity_id": "string",
    "market_domain_code": "string"
  },
  "project": {
    "project_id": "string",
    "partition_id": "string"
  },
  "decision": {
    "title": "string",
    "summary": "string",
    "decision_class": "strategic|tactical|operational|safety|financial|other",
    "confidence": "low|medium|high",
    "alternatives_considered": ["string"]
  },
  "context_refs": {
    "state_snapshot_ref": "content-id-or-internal-ref",
    "evidence_refs": ["content-id-or-internal-ref"]
  },
  "constraints_in_force": {
    "scope_profile_id": "string",
    "constraint_profile_id": "string",
    "export_class": "C0|C1|C2",
    "energy_cap_ref": "energy_budget.json#time_window"
  },
  "owner": {
    "decision_owner_type": "human|ai_assisted|committee",
    "approver_ref": "string"
  },
  "privacy": {
    "contains_personal_data": false,
    "contains_sensitive_trade_info": false
  },
  "integrity": {
    "witness_id": "optional-wit-id",
    "hash_commitment": "optional"
  }
}
```

---

## 4) Guardrails (hard rules)

### 4.1 No raw personal data (required)
CDM MUST NOT store:
- PII (names, addresses, SSNs, emails of individuals)
- student records, medical records, etc.

Instead store **counts**, **roles**, **anonymized identifiers**, or references to secured systems.

### 4.2 No actionable market signals (required)
CDM MUST NOT be used to publish:
- “buy/sell/entry/exit” guidance
- time-sensitive signals
- per-asset/per-trade instructions

### 4.3 “Reference not payload” (required)
Context should be stored as **refs**, not copied payloads:
- state_snapshot_ref points to PP-local storage (or derived summary)
- evidence_refs refer to documents/logs in PP

### 4.4 Append-only bias (recommended)
Edits should be rare; prefer new records that supersede old ones:
- use `supersedes_record_ids` (optional field) rather than overwriting.

---

## 5) How CDM boosts business function capability
CDM enables:
- repeatable decision-making workflows
- post-mortems with real context
- faster onboarding (“how we decide here”)
- risk control (what constraints were in force?)
- measured iteration without data bloat

---

## 6) Integration points (fits the existing framework)
- Entity Sandbox → Project Partition → Modality Enclaves
- CDM lives PP-local (project scoped)
- CTL exports can reference CDM records only as **pattern-level** summaries (C1) if needed
- On-chain WIT can optionally anchor **integrity** of key CDM records (commitment only)

---

## 7) Conformance requirements (v0.1)
A CDM deployment claims compliance only if:
- record schema validates
- no raw PII fields present
- no action-signal language present
- context stored by reference, not copied payloads

---

## 8) Outcome linking (v0.1)

### 8.1 OutcomeRecord (recommended)
An OutcomeRecord captures follow-up results **without editing** the original DecisionRecord.

Minimal shape:

```json
{
  "cdm_v": "0.1",
  "record_type": "outcome",
  "record_id": "uuid",
  "time_utc": "RFC3339",
  "entity": { "entity_id": "string", "market_domain_code": "string" },
  "project": { "project_id": "string", "partition_id": "string" },
  "links": {
    "decision_record_id": "uuid",
    "related_record_ids": ["uuid"]
  },
  "outcome": {
    "status": "positive|negative|mixed|unknown",
    "summary": "string",
    "observed_metrics": [
      { "name": "string", "value": "number-or-string", "unit": "string", "time_window": "string" }
    ],
    "evidence_refs": ["content-id-or-internal-ref"]
  },
  "privacy": { "contains_personal_data": false, "contains_sensitive_trade_info": false }
}
```

### 8.2 Outcome linking rules (normative)
- OutcomeRecord MUST reference the DecisionRecord via `links.decision_record_id`.
- OutcomeRecord MUST NOT restate raw telemetry; use `observed_metrics` + `evidence_refs`.
- OutcomeRecord MAY be published through CTL only as **C1 pattern-level** summaries (if needed).

---

## 9) Supersession mechanics (v0.1)

### 9.1 Why supersession exists
When a decision changes, do not overwrite history. Create a new DecisionRecord that **supersedes** the old one.

### 9.2 Supersession fields (recommended)
Add a `supersedes_record_ids` array at top-level:

```json
"supersedes_record_ids": ["prior-record-id"]
```

### 9.3 Supersession rules (normative)
- Records MUST be append-only by default.
- If a record is “revised,” the new record MUST include `supersedes_record_ids`.
- A record MUST NOT supersede records from a different project partition.
- A record MUST NOT create a circular supersession chain.

