from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set

"""
cdm_ledger_validator.py

Validates a folder of CDM records (JSON files) for:
- Schema-ish invariants (minimal required fields present)
- No circular supersession chains
- No cross-partition supersession (same project.partition_id required)
- Outcomes link to existing decision records
- No self-supersession
- Optional: basic duplicate record_id detection

Usage:
  python conformance/cdm_ledger_validator.py path/to/cdm_records_folder

Expected:
  Folder contains *.json records; non-JSON files ignored.
"""

REQUIRED_TOP = {"cdm_v","record_type","record_id","time_utc","entity","project","privacy"}
VALID_TYPES = {"decision","outcome","assumption","constraint"}

class ValidationError(Exception):
    pass

def load_records(folder: Path) -> List[dict]:
    records = []
    for p in sorted(folder.rglob("*.json")):
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("cdm_v") == "0.1":
                data["_source_path"] = str(p)
                records.append(data)
        except Exception:
            # ignore parse errors here; treat as non-record file
            continue
    return records

def key(record: dict) -> Tuple[str,str,str]:
    # (project_id, partition_id, record_id)
    proj = record.get("project", {})
    return (proj.get("project_id",""), proj.get("partition_id",""), record.get("record_id",""))

def basic_checks(records: List[dict]) -> None:
    seen_ids: Set[str] = set()
    for r in records:
        src = r.get("_source_path","<unknown>")
        missing = [k for k in REQUIRED_TOP if k not in r]
        if missing:
            raise ValidationError(f"{src}: missing required fields: {missing}")
        if r.get("record_type") not in VALID_TYPES:
            raise ValidationError(f"{src}: invalid record_type: {r.get('record_type')}")
        rid = r.get("record_id")
        if not isinstance(rid, str) or not rid.strip():
            raise ValidationError(f"{src}: invalid record_id")
        if rid in seen_ids:
            raise ValidationError(f"{src}: duplicate record_id detected: {rid}")
        seen_ids.add(rid)

        proj = r.get("project", {})
        if not proj.get("project_id") or not proj.get("partition_id"):
            raise ValidationError(f"{src}: missing project_id/partition_id")

        if r.get("cdm_v") != "0.1":
            raise ValidationError(f"{src}: unsupported cdm_v: {r.get('cdm_v')}")

        supers = r.get("supersedes_record_ids") or []
        if rid in supers:
            raise ValidationError(f"{src}: record supersedes itself (circular)")

def build_index(records: List[dict]) -> Dict[str, dict]:
    # index by record_id
    idx = {}
    for r in records:
        idx[r["record_id"]] = r
    return idx

def check_outcome_links(records: List[dict], idx: Dict[str, dict]) -> None:
    for r in records:
        if r.get("record_type") != "outcome":
            continue
        src = r.get("_source_path","<unknown>")
        links = r.get("links") or {}
        dec_id = links.get("decision_record_id")
        if not dec_id:
            raise ValidationError(f"{src}: outcome missing links.decision_record_id")
        dec = idx.get(dec_id)
        if not dec:
            raise ValidationError(f"{src}: outcome links to missing decision_record_id: {dec_id}")
        if dec.get("record_type") != "decision":
            raise ValidationError(f"{src}: linked decision_record_id is not a decision: {dec_id}")

        # Ensure same partition
        if dec.get("project", {}).get("partition_id") != r.get("project", {}).get("partition_id"):
            raise ValidationError(f"{src}: outcome links across partitions (not allowed)")

def check_cross_partition_supersession(records: List[dict], idx: Dict[str, dict]) -> None:
    for r in records:
        supers = r.get("supersedes_record_ids") or []
        if not supers:
            continue
        src = r.get("_source_path","<unknown>")
        my_part = r.get("project", {}).get("partition_id")
        for s in supers:
            target = idx.get(s)
            if not target:
                raise ValidationError(f"{src}: supersedes missing record_id: {s}")
            targ_part = target.get("project", {}).get("partition_id")
            if my_part != targ_part:
                raise ValidationError(f"{src}: cross-partition supersession not allowed: {s}")

def detect_cycles(records: List[dict], idx: Dict[str, dict]) -> None:
    """Detect cycles in supersession graph across all records."""
    # Build adjacency: record -> superseded records
    adj: Dict[str, List[str]] = {}
    for r in records:
        rid = r["record_id"]
        supers = r.get("supersedes_record_ids") or []
        adj[rid] = list(supers)

    WHITE, GRAY, BLACK = 0, 1, 2
    color: Dict[str, int] = {rid: WHITE for rid in adj.keys()}
    stack: List[str] = []

    def dfs(u: str):
        color[u] = GRAY
        stack.append(u)
        for v in adj.get(u, []):
            if v not in color:
                continue
            if color[v] == GRAY:
                # cycle found
                cycle_start = stack.index(v)
                cycle = stack[cycle_start:] + [v]
                src = idx.get(u, {}).get("_source_path","<unknown>")
                raise ValidationError(f"{src}: circular supersession chain detected: {' -> '.join(cycle)}")
            if color[v] == WHITE:
                dfs(v)
        stack.pop()
        color[u] = BLACK

    for node in list(adj.keys()):
        if color[node] == WHITE:
            dfs(node)

def main():
    if len(sys.argv) != 2:
        print("Usage: python conformance/cdm_ledger_validator.py path/to/cdm_records_folder")
        sys.exit(2)

    folder = Path(sys.argv[1])
    if not folder.exists() or not folder.is_dir():
        raise SystemExit("FAIL: provided path is not a folder")

    records = load_records(folder)
    if not records:
        raise SystemExit("FAIL: no CDM v0.1 records found")

    idx = build_index(records)

    basic_checks(records)
    check_outcome_links(records, idx)
    check_cross_partition_supersession(records, idx)
    detect_cycles(records, idx)

    print(f"OK: validated {len(records)} CDM records with no linkage/supersession violations")

if __name__ == "__main__":
    try:
        main()
    except ValidationError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
