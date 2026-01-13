from __future__ import annotations
import json
import re
import sys
from pathlib import Path

# Heuristic: disallow common PII-ish keys anywhere in CDM records.
PII_KEY_HINTS = {
    "name", "first_name", "last_name", "email", "phone", "address", "ssn",
    "dob", "birthdate", "student_id", "medical", "diagnosis"
}

ACTION_PATTERNS = [
    r"\b(buy|sell|long|short|entry|exit|stop[- ]loss|take[- ]profit)\b",
    r"\b(signal|alpha|edge|front[- ]run|arbitrage)\b",
    r"\b(today|now|immediately|urgent|right away)\b",
]

def walk(obj):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield ("key", k)
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)
    elif isinstance(obj, str):
        yield ("text", obj)

def assert_outcome_links(data: dict):
    if data.get("record_type") == "outcome":
        links = data.get("links", {})
        if not links.get("decision_record_id"):
            raise SystemExit("FAIL: outcome record missing links.decision_record_id")

def assert_no_circular_supersession(data: dict):
    # Single-record check: prevent self-supersession
    supers = data.get("supersedes_record_ids") or []
    rid = data.get("record_id")
    if rid and rid in supers:
        raise SystemExit("FAIL: record supersedes itself (circular)")

def main():
    p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("cdm_example_record.json")
    data = json.loads(p.read_text(encoding="utf-8"))

    assert_outcome_links(data)
    assert_no_circular_supersession(data)

    # Key-based PII heuristic
    for typ, val in walk(data):
        if typ == "key":
            if val.lower() in PII_KEY_HINTS:
                raise SystemExit(f"FAIL: PII-like key detected in CDM: {val}")

    # Action/signal language heuristic
    for typ, val in walk(data):
        if typ == "text":
            t = val.lower()
            for pat in ACTION_PATTERNS:
                if re.search(pat, t):
                    raise SystemExit(f"FAIL: action/signal language detected: {pat}")

    print("OK: CDM record passes basic PII and signal-drift lint")

if __name__ == "__main__":
    main()
