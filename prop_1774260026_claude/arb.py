#!/usr/bin/env python3
"""arb.py - tools for the AI Agent Autonomy Restrictions Benchmark (standard library only).

Usage:
  python arb.py validate [DATASET] [SCHEMA]       check the dataset against schema.json and the extra rules
  python arb.py stats    [DATASET] [--by FIELD]   restriction pressure per jurisdiction / initiator / agent_class / ...
  python arb.py score    PREDICTIONS [DATASET]    score a model's predictions on the annotation task
  python arb.py task     [DATASET]                print the annotation task inputs (id, system, summary) as JSON

DATASET defaults to ai_agent_restrictions_benchmark.json and SCHEMA to schema.json, both next to this file.

PREDICTIONS is a JSON object mapping entry id -> {"severity": int, "restriction_type": str,
"initiator_type": str}; any subset of fields may be given.
"""
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_DATA = HERE / "ai_agent_restrictions_benchmark.json"
DEFAULT_SCHEMA = HERE / "schema.json"
MIN_ENTRIES = 50
MIN_DISTINCT_PLACES = 10


def load(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _check_value(value, spec, where, errors):
    """Check one value against the subset of JSON Schema used by schema.json."""
    if "enum" in spec and value not in spec["enum"]:
        errors.append(f"{where}: {value!r} is not one of {spec['enum']}")
        return
    t = spec.get("type")
    if t == "string":
        if not isinstance(value, str):
            errors.append(f"{where}: expected string")
            return
        if len(value) < spec.get("minLength", 0):
            errors.append(f"{where}: shorter than {spec['minLength']} characters")
        if "pattern" in spec and not re.search(spec["pattern"], value):
            errors.append(f"{where}: {value!r} does not match {spec['pattern']}")
    elif t == "integer":
        if not isinstance(value, int) or isinstance(value, bool):
            errors.append(f"{where}: expected integer")
            return
        if value < spec.get("minimum", value) or value > spec.get("maximum", value):
            errors.append(f"{where}: {value} outside {spec.get('minimum')}..{spec.get('maximum')}")
    elif t == "array":
        if not isinstance(value, list):
            errors.append(f"{where}: expected array")
            return
        if len(value) < spec.get("minItems", 0):
            errors.append(f"{where}: needs at least {spec['minItems']} item(s)")
        if spec.get("uniqueItems") and len(value) != len({json.dumps(v, sort_keys=True) for v in value}):
            errors.append(f"{where}: items must be unique")
        if "items" in spec:
            for i, item in enumerate(value):
                _check_value(item, spec["items"], f"{where}[{i}]", errors)
    elif t == "object":
        if not isinstance(value, dict):
            errors.append(f"{where}: expected object")
            return
        for key in spec.get("required", []):
            if key not in value:
                errors.append(f"{where}: missing required field {key!r}")
        props = spec.get("properties", {})
        if spec.get("additionalProperties") is False:
            for key in value:
                if key not in props:
                    errors.append(f"{where}: unexpected field {key!r}")
        for key, sub in props.items():
            if key in value:
                _check_value(value[key], sub, f"{where}.{key}", errors)


def validate(data, schema):
    """Return a list of error strings (empty means valid)."""
    errors = []
    entry_spec = schema["$defs"]["entry"]
    for key in schema.get("required", []):
        if key not in data:
            errors.append(f"dataset: missing {key!r}")
    entries = data.get("entries", [])
    if len(entries) < MIN_ENTRIES:
        errors.append(f"dataset: {len(entries)} entries, need at least {MIN_ENTRIES}")
    scale = data.get("severity_scale", {})
    for level in "12345":
        if level not in scale:
            errors.append(f"severity_scale: missing level {level}")

    seen_ids, seen_urls = set(), Counter()
    for i, e in enumerate(entries):
        where = f"entries[{i}]" + (f" ({e.get('id')})" if isinstance(e, dict) and e.get("id") else "")
        _check_value(e, entry_spec, where, errors)
        if not isinstance(e, dict):
            continue
        eid = e.get("id")
        if eid in seen_ids:
            errors.append(f"{where}: duplicate id")
        seen_ids.add(eid)
        # date_precision must agree with how much of the date is given
        date, prec = e.get("date", ""), e.get("date_precision")
        parts = len(date.split("-")) if isinstance(date, str) else 0
        expected = {1: {"year"}, 2: {"month"}, 3: {"day", "approximate"}}.get(parts, set())
        if prec and prec not in expected:
            errors.append(f"{where}: date {date!r} does not fit precision {prec!r}")
        if parts == 3:
            y, m, d = (int(x) for x in date.split("-"))
            if not (1 <= m <= 12 and 1 <= d <= 31):
                errors.append(f"{where}: impossible date {date!r}")
        for s in e.get("sources", []):
            if isinstance(s, dict) and "url" in s:
                seen_urls[(eid, s["url"])] += 1
    for (eid, url), n in seen_urls.items():
        if n > 1:
            errors.append(f"{eid}: source listed twice: {url}")
    places = {e.get("jurisdiction") for e in entries if isinstance(e, dict)}
    entities = {e.get("platform_or_entity") for e in entries if isinstance(e, dict)}
    if len(places - {"GLOBAL"}) + len(entities) < MIN_DISTINCT_PLACES:
        errors.append("dataset: fewer than 10 distinct platforms/jurisdictions")
    return errors


def stats(data, by="jurisdiction"):
    """Restriction pressure per group: count, mean severity, severity sum, share of hard (>=4) restrictions."""
    groups = defaultdict(list)
    for e in data["entries"]:
        groups[e[by]].append(e["severity"])
    rows = []
    for key, sev in groups.items():
        rows.append({
            by: key,
            "count": len(sev),
            "mean_severity": round(sum(sev) / len(sev), 2),
            "pressure_index": sum(sev),
            "hard_share": round(sum(1 for s in sev if s >= 4) / len(sev), 2),
        })
    rows.sort(key=lambda r: (-r["pressure_index"], str(r[by])))
    return rows


def task_inputs(data):
    """The fields a model sees when asked to annotate an incident."""
    return [{"id": e["id"], "system": e["system"], "platform_or_entity": e["platform_or_entity"],
             "summary": e["summary"], "stated_justification": e["stated_justification"]}
            for e in data["entries"]]


def score(predictions, data):
    """Compare predicted labels with the gold annotations."""
    gold = {e["id"]: e for e in data["entries"]}
    result = {"n_predicted": 0, "unknown_ids": []}
    abs_err, within1 = [], 0
    exact = Counter()
    totals = Counter()
    for eid, pred in predictions.items():
        if eid not in gold:
            result["unknown_ids"].append(eid)
            continue
        result["n_predicted"] += 1
        g = gold[eid]
        if "severity" in pred:
            err = abs(int(pred["severity"]) - g["severity"])
            abs_err.append(err)
            within1 += err <= 1
        for field in ("restriction_type", "initiator_type", "agent_class"):
            if field in pred:
                totals[field] += 1
                exact[field] += pred[field] == g[field]
    if abs_err:
        result["severity_mae"] = round(sum(abs_err) / len(abs_err), 3)
        result["severity_within_1"] = round(within1 / len(abs_err), 3)
    for field, n in totals.items():
        result[f"{field}_accuracy"] = round(exact[field] / n, 3)
    result["coverage"] = round(result["n_predicted"] / len(gold), 3)
    return result


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    if cmd == "validate":
        data = load(rest[0] if rest else DEFAULT_DATA)
        schema = load(rest[1] if len(rest) > 1 else DEFAULT_SCHEMA)
        errors = validate(data, schema)
        for err in errors:
            print("ERROR", err)
        n = len(data.get("entries", []))
        places = len({e.get("jurisdiction") for e in data.get("entries", [])})
        ents = len({e.get("platform_or_entity") for e in data.get("entries", [])})
        print(f"{'INVALID' if errors else 'OK'}: {n} entries, {ents} restricting entities, {places} jurisdiction codes")
        return 1 if errors else 0
    if cmd == "stats":
        by = "jurisdiction"
        if "--by" in rest:
            by = rest[rest.index("--by") + 1]
            rest = [a for a in rest if a not in ("--by", by)]
        data = load(rest[0] if rest else DEFAULT_DATA)
        if by not in data["entries"][0]:
            print(f"unknown field {by!r}")
            return 2
        print(json.dumps(stats(data, by), indent=2, ensure_ascii=False))
        return 0
    if cmd == "task":
        data = load(rest[0] if rest else DEFAULT_DATA)
        print(json.dumps(task_inputs(data), indent=2, ensure_ascii=False))
        return 0
    if cmd == "score":
        if not rest:
            print("score needs a predictions file")
            return 2
        preds = load(rest[0])
        data = load(rest[1] if len(rest) > 1 else DEFAULT_DATA)
        print(json.dumps(score(preds, data), indent=2))
        return 0
    print(f"unknown command {cmd!r}\n{__doc__}")
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
