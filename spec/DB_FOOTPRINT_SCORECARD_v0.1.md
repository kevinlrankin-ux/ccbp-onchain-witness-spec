# DB Footprint Scorecard (v0.1)
*(Inspectability tool for DB-minimizing architectures)*

**Status:** Draft  
**Purpose:** Give entities a clear, non-punitive way to understand how efficiently they are using databases versus edge/query capabilities—and where expansion can occur without cost explosions.

---

## 1) Why this scorecard exists
Most teams don’t know:
- how much data they *store but never use*
- how much could be answered from live state
- when DB growth is a choice vs a habit

This scorecard makes DB usage **visible, optional, and improvable**—not a compliance weapon.

---

## 2) Core metrics (v0.1)

### A) Persistence Ratio
**What % of raw telemetry is persisted long-term**

```
persisted_events / total_events
```

**Interpretation**
- 0–20% → DB-minimal, edge-first
- 20–50% → hybrid
- 50%+ → DB-heavy (review necessity)

---

### B) Rollup Efficiency
**How much raw data collapses into rollups**

```
raw_events / rollup_records
```

Higher is better (means fewer rows for same insight).

---

### C) Query Resolution Source
**Where answers come from**

- % answered from state store
- % answered via live device query
- % answered from DB

Target: majority from **state + live**, not DB.

---

### D) Cost per Answer
**Infrastructure cost divided by successful queries**

This reframes cost as *useful answers*, not storage volume.

---

### E) Staleness Rate
**How often answers are stale**

```
stale_answers / total_answers
```

High staleness = either missing live queries or over-reliance on DB snapshots.

---

### F) DB Growth Velocity
**Change in DB size per time window**

Helps catch silent cost creep early.

---

## 3) Qualitative flags (simple but powerful)

- “Raw telemetry stored by default” ❌
- “Rollups defined per Market/Domain” ✅
- “State freshness policy enforced” ✅
- “Edge aggregation enabled” ✅
- “DB schema changes required to add new device type” ❌

---

## 4) Output format (example)
```json
{
  "scorecard_v": "0.1",
  "time_window": "2026-01",
  "persistence_ratio": 0.18,
  "rollup_efficiency": 240,
  "query_resolution": {
    "state_store": 0.52,
    "live_query": 0.31,
    "database": 0.17
  },
  "cost_per_answer_usd": 0.004,
  "staleness_rate": 0.06,
  "db_growth_gb_month": 12,
  "flags": {
    "raw_by_default": false,
    "edge_aggregation": true,
    "schema_lock_in": false
  }
}
```

---

## 5) Guardrails
- Scorecard MUST NOT be used for penalties.
- Scorecard MUST NOT be published externally by default.
- Purpose is **internal optimization + design awareness**.

---

## 6) How it ties into the “secret sauce”
The scorecard turns “less DB” from an opinion into:
- a measurable design choice
- a competitive advantage
- a cultural norm (“we earn persistence”)

