# Edge-Query + Context Broker Architecture (v0.1)
*(DB-Minimizing “Ask the Environment” Design — Secret Sauce Addendum)*

**Status:** Draft  
**Goal:** Minimize owned database footprint while preserving **expansion capacity** and a natural-language “ask for what you need” interface for human + AI users.

> **Core idea:** Treat databases as *optional memory*, not the source of truth. The source of truth is the **edge/device state** + **event stream**.

---

## 1) What this adds to the framework
This addendum defines a **DB-minimizing query plane** that fits inside the Entity Sandbox model:

- Devices/edge hold *fresh truth*
- A Context Broker answers most questions using **live state**
- Databases are used selectively for **history, audits, and analytics**
- Expansion happens by adding devices/projects without “DB first” redesigns

---

## 2) The “Less DB to Own” pattern

### 2.1 Replace “write everything” with “store only what’s valuable”
**Default:** do NOT persist every sensor reading. Persist:
- aggregates (5-min/1-hr rollups)
- exceptions (alarms, threshold crossings)
- audit events (configuration changes, control actions)
- business outcomes (completed jobs, energy totals)

### 2.2 Use a lightweight **State Store** instead of a heavy relational DB
Maintain **current state** in a small key/value or document store (or in-memory cache with persistence):
- last known value
- timestamp
- quality/validity
- provenance tags

This store is not your “database of record.” It’s your “now.”

### 2.3 Make “history” optional and modular
If/when you need history:
- time-series store for telemetry
- object storage for bulky artifacts
- relational DB only for small, high-integrity business tables (users, billing, entities, scopes)

---

## 3) Reference architecture (minimal components)

### Layer A — Edge/Device Plane (truth-now)
- sensors, PLCs, gateways
- local buffering + aggregation
- publish on change (event-driven)

### Layer B — Event Bus (routing)
- MQTT / Kafka / AMQP
- normalizes device updates and delivers to subscribers

### Layer C — Context Broker (query plane)
- device registry + metadata (“what is Room 214?”)
- state store (“what’s the last known value?”)
- live query fallback (“if stale, ask device/gateway now”)
- authorization + rate limiting

### Layer D — Persistence (optional memory)
- time-series DB (rollups, exceptions)
- object store (logs, artifacts)
- relational DB (entity registry, subscriptions, policy references)

### Layer E — Natural-language interface
- “Ask the environment” → translator → safe query plan
- read-only by default; actions require explicit authorization

---

## 4) The expansion advantage
This architecture scales by adding *more producers* (devices/projects) without forcing a DB schema expansion per device type.

### Expansion stays cheap because:
- new devices register metadata; no schema migration
- most queries hit state store or live device queries
- history storage is selective and can be turned up later

---

## 5) Query types and where they should resolve

### Q1: “What is happening now?” (most common)
Resolve via:
- state store (fast)
- live device query if stale

### Q2: “Notify me when X happens”
Resolve via:
- event bus subscriptions
- rules at edge/gateway when possible

### Q3: “What happened last week/month?”
Resolve via:
- time-series rollups + exception logs (minimal DB)
- do not backfill raw telemetry unless required

### Q4: “Prove it / audit it”
Resolve via:
- event logs
- optional on-chain witness (commitment-only) for integrity and provenance

---

## 6) Why it’s “secret sauce”
Many build-outs start DB-first and get trapped:
- huge ingestion costs
- storage growth nobody uses
- schema churn
- fragile analytics pipelines

This pattern flips it:
- compute and storage are *earned*, not assumed
- the system remains usable when data is sparse
- expansion is operationally simple
- AI + humans can query “now” without heavy data warehousing

---

## 7) Guardrails (to keep it sane)
- **Freshness policy:** if state older than N seconds/minutes, mark stale and query live or disclose staleness.
- **Rate limits:** prevent NL querying from becoming a device DoS.
- **Read-only default:** no device control unless explicitly authorized.
- **Minimal persistence defaults:** rollups + exceptions + audits.

---

## 8) Suggested config artifacts (optional)
- `device_registry.yaml`
- `state_freshness_policy.yaml`
- `telemetry_persistence_policy.yaml` (rollups/exceptions)
- `query_rate_limits.yaml`
