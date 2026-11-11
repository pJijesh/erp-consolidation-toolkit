"""A go or no go style readiness scorecard built from the other commands' summary files.

The thresholds are judgement-based starting points, not industry standards. They are
documented in docs/readiness-thresholds.md and can be overridden with a JSON file.
"""

from __future__ import annotations

import copy

from .errors import InputError

LOWER, HIGHER = "lower", "higher"

# metric key -> direction, green limit, amber limit, short description
DEFAULT_THRESHOLDS: dict[str, dict] = {
    "profile.required_missing_rate": {"direction": LOWER, "green": 0.02, "amber": 0.05,
                                      "description": "Highest missing rate among required columns"},
    "profile.key_duplicate_rate": {"direction": LOWER, "green": 0.0, "amber": 0.005,
                                   "description": "Share of rows whose key value appears more than once"},
    "profile.format_invalid_rate": {"direction": LOWER, "green": 0.01, "amber": 0.05,
                                    "description": "Share of checked values that fail a format check"},
    "coa.approved_coverage": {"direction": HIGHER, "green": 0.98, "amber": 0.90,
                              "description": "Share of source accounts with an approved mapping"},
    "coa.balance_accounts_not_approved": {"direction": LOWER, "green": 0, "amber": 0,
                                          "description": "Accounts carrying a balance without an approved mapping"},
    "coa.error_exceptions": {"direction": LOWER, "green": 0, "amber": 0,
                             "description": "Mapping exceptions at error severity"},
    "dedupe.within_duplicate_rate": {"direction": LOWER, "green": 0.01, "amber": 0.03,
                                     "description": "Share of one system's records that would be merged into another record of the same system"},
    "dedupe.review_pairs_per_100_records": {"direction": LOWER, "green": 3, "amber": 8,
                                            "description": "Pairs needing human review per 100 records (workload)"},
    "reconcile.periods_with_differences": {"direction": LOWER, "green": 0, "amber": 0,
                                           "description": "Periods where the mapped trial balance differs beyond tolerance"},
}

REQUIRED_KINDS = {"profile": "data quality profile", "coa": "chart of accounts mapping", "dedupe": "duplicate analysis"}


def load_thresholds(overrides: dict | None) -> dict[str, dict]:
    """Return the default thresholds with any overrides applied, checking them first."""
    merged = copy.deepcopy(DEFAULT_THRESHOLDS)
    for key, val in (overrides or {}).items():
        if key not in merged:
            raise InputError(f"Unknown threshold '{key}'. Known: {', '.join(sorted(merged))}.")
        if not isinstance(val, dict) or not {"green", "amber"} <= set(val) or set(val) - {"green", "amber"}:
            raise InputError(f"Threshold '{key}' must look like {{\"green\": number, \"amber\": number}}.")
        for k in ("green", "amber"):
            if not isinstance(val[k], (int, float)) or isinstance(val[k], bool):
                raise InputError(f"Threshold '{key}.{k}' must be a number.")
        g, a = val["green"], val["amber"]
        ok = g <= a if merged[key]["direction"] == LOWER else g >= a
        if not ok:
            word = "no greater than" if merged[key]["direction"] == LOWER else "no less than"
            raise InputError(f"Threshold '{key}': green must be {word} amber.")
        merged[key]["green"], merged[key]["amber"] = g, a
    return merged


def _status(value: float, spec: dict) -> str:
    g, a = spec["green"], spec["amber"]
    if spec["direction"] == LOWER:
        return "GREEN" if value <= g else "AMBER" if value <= a else "RED"
    return "GREEN" if value >= g else "AMBER" if value >= a else "RED"


def _fmt(metric: str, value: float) -> str:
    if metric.endswith("_rate") or metric.endswith("_coverage"):
        return f"{value * 100:.1f}%"
    return f"{value:g}"


def evaluate(summaries: list[dict], thresholds: dict[str, dict]) -> dict:
    checks: list[dict] = []
    not_assessed: list[str] = []

    def add(area: str, subject: str, metric: str, value) -> None:
        spec = thresholds[metric]
        if value is None:
            not_assessed.append(f"{subject}: {spec['description']}")
            return
        checks.append({
            "area": area, "subject": subject, "metric": metric, "description": spec["description"],
            "value": value, "display": _fmt(metric, value), "green": spec["green"], "amber": spec["amber"],
            "direction": spec["direction"], "status": _status(value, spec),
        })

    kinds_seen: set[str] = set()
    for s in summaries:
        kind = s.get("kind")
        kinds_seen.add(kind)
        name = s.get("name") or s.get("dataset") or kind
        if kind == "profile":
            add("Data quality", name, "profile.required_missing_rate", s.get("required_max_missing_rate"))
            add("Data quality", name, "profile.key_duplicate_rate", s.get("key_duplicate_rate"))
            add("Data quality", name, "profile.format_invalid_rate", s.get("format_invalid_rate"))
        elif kind == "coa":
            add("Chart of accounts", name, "coa.approved_coverage", s["approved_coverage"])
            add("Chart of accounts", name, "coa.balance_accounts_not_approved", s.get("balance_accounts_not_approved"))
            add("Chart of accounts", name, "coa.error_exceptions", s["exceptions_error"])
        elif kind == "dedupe":
            for key in sorted(s["systems"]):
                st = s["systems"][key]
                add("Duplicates", f"{name}, {st['label']}", "dedupe.within_duplicate_rate", st["within_duplicate_rate"])
            add("Duplicates", name, "dedupe.review_pairs_per_100_records", s["review_pairs_per_100_records"])
        elif kind == "reconcile":
            add("Reconciliation", name, "reconcile.periods_with_differences", s["periods_with_differences"])
        else:
            raise InputError(f"Unrecognised summary file (kind '{kind}'). Pass the JSON summaries written by profile, map-coa, dedupe and reconcile.")

    missing = sorted(REQUIRED_KINDS[k] for k in REQUIRED_KINDS if k not in kinds_seen)
    reds = [c for c in checks if c["status"] == "RED"]
    ambers = [c for c in checks if c["status"] == "AMBER"]
    if missing or reds:
        verdict = "NO-GO"
    elif ambers:
        verdict = "CONDITIONAL GO"
    else:
        verdict = "GO"
    return {
        "kind": "readiness",
        "verdict": verdict,
        "red": len(reds), "amber": len(ambers), "green": sum(1 for c in checks if c["status"] == "GREEN"),
        "missing_evidence": missing,
        "not_assessed": sorted(not_assessed),
        "checks": checks,
    }


def render_markdown(result: dict, thresholds: dict[str, dict]) -> str:
    lines = ["# Readiness scorecard", "", f"**Verdict: {result['verdict']}**", ""]
    lines += [f"- Red: {result['red']}; amber: {result['amber']}; green: {result['green']}"]
    if result["missing_evidence"]:
        lines.append(f"- Evidence missing, so the verdict cannot be better than NO-GO: {', '.join(result['missing_evidence'])}")
    lines += ["", "Rule: any red check, or missing evidence, gives NO-GO. Otherwise any amber check gives CONDITIONAL GO, "
              "and each amber check is a condition to close before cutover. Otherwise GO. "
              "The scorecard reports on the files supplied only. It is an input to a human decision, not the decision.", ""]
    order = {"RED": 0, "AMBER": 1, "GREEN": 2}
    lines += ["## Checks", "", "| Status | Area | Subject | Measure | Value | Green | Amber |", "|---|---|---|---|---:|---:|---:|"]
    for c in sorted(result["checks"], key=lambda c: (order[c["status"]], c["area"], c["subject"], c["metric"])):
        cmp_ = "at most" if c["direction"] == LOWER else "at least"
        lines.append(f"| {c['status']} | {c['area']} | {c['subject']} | {c['description']} | {c['display']} | "
                     f"{cmp_} {_fmt(c['metric'], c['green'])} | {cmp_} {_fmt(c['metric'], c['amber'])} |")
    if result["not_assessed"]:
        lines += ["", "## Not assessed", "", "These measures were not available in the files supplied, for example because no key column was given:", ""]
        lines += [f"- {n}" for n in result["not_assessed"]]
    return "\n".join(lines)
