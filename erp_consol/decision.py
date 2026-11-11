"""Scored decision framework: consolidate, partially integrate, or keep separate.

The criteria, weights and scale anchors live in decision/criteria.csv so they can be
read and changed without touching code. The method is documented in decision/README.md.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from .csvio import read_table
from .errors import InputError

CASE_CONSOLIDATE = 65.0
ABILITY_CONSOLIDATE = 60.0
CASE_PARTIAL = 40.0

OUTCOMES = ("DEFER", "KEEP SEPARATE", "PARTIALLY INTEGRATE", "CONSOLIDATE")


@dataclass
class Item:
    id: str
    kind: str  # criterion or gate
    axis: str  # case or ability for criteria, empty for gates
    name: str
    weight: int
    question: str
    anchors: dict[str, str]
    effect: str  # for gates: defer or cap_partial


def default_criteria_path() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(os.path.dirname(here), "decision", "criteria.csv")


def load_criteria(path: str) -> list[Item]:
    table = read_table(path)
    real = table.resolve(["id", "kind", "axis", "name", "weight", "question", "score_1", "score_3", "score_5", "effect"])
    items: list[Item] = []
    seen: set[str] = set()
    for row, line in zip(table.rows, table.lines):
        g = lambda k: row[real[k]].strip()
        kind = g("kind")
        if kind not in ("criterion", "gate"):
            raise InputError(f"{table.name}: line {line}: kind must be 'criterion' or 'gate'.")
        if g("id") in seen:
            raise InputError(f"{table.name}: line {line}: duplicate id '{g('id')}'.")
        seen.add(g("id"))
        axis, effect, weight = g("axis"), g("effect"), 0
        if kind == "criterion":
            if axis not in ("case", "ability"):
                raise InputError(f"{table.name}: line {line}: axis must be 'case' or 'ability'.")
            try:
                weight = int(g("weight"))
            except ValueError:
                raise InputError(f"{table.name}: line {line}: weight must be a whole number.") from None
            if weight < 1:
                raise InputError(f"{table.name}: line {line}: weight must be 1 or more.")
        elif effect not in ("defer", "cap_partial"):
            raise InputError(f"{table.name}: line {line}: a gate needs effect 'defer' or 'cap_partial'.")
        items.append(Item(g("id"), kind, axis, g("name"), weight, g("question"),
                          {"1": g("score_1"), "3": g("score_3"), "5": g("score_5")}, effect))
    return items


def load_scores(path: str, items: list[Item]) -> tuple[dict[str, str], dict[str, str], list[str]]:
    table = read_table(path)
    real = table.resolve(["id", "value"])
    ev_col = table.find_column("evidence")
    known = {i.id: i for i in items}
    values: dict[str, str] = {}
    evidence: dict[str, str] = {}
    problems: list[str] = []
    for row, line in zip(table.rows, table.lines):
        rid = row[real["id"]].strip()
        val = row[real["value"]].strip().lower()
        if rid not in known:
            problems.append(f"line {line}: unknown id '{rid}'")
            continue
        if rid in values:
            problems.append(f"line {line}: '{rid}' appears twice")
            continue
        item = known[rid]
        if item.kind == "criterion":
            if val not in ("1", "2", "3", "4", "5"):
                problems.append(f"line {line}: {rid} needs a score from 1 to 5, found '{row[real['value']]}'")
                continue
        elif val not in ("yes", "no"):
            problems.append(f"line {line}: {rid} is a gate and needs yes or no, found '{row[real['value']]}'")
            continue
        values[rid] = val
        evidence[rid] = row[ev_col].strip() if ev_col else ""
    missing = [i.id for i in items if i.id not in values]
    if missing:
        problems.append("no value for " + ", ".join(missing))
    if problems:
        raise InputError(f"{table.name}: " + "; ".join(problems[:8]) + (f"; and {len(problems) - 8} more" if len(problems) > 8 else "") + ".")
    warnings = [f"No evidence recorded for {i.id} ({i.name})." for i in items if not evidence.get(i.id)]
    return values, evidence, warnings


def axis_score(items: list[Item], values: dict[str, str], axis: str) -> float:
    crit = [i for i in items if i.kind == "criterion" and i.axis == axis]
    total = sum(i.weight for i in crit)
    got = sum(i.weight * (int(values[i.id]) - 1) / 4 for i in crit)
    return round(100 * got / total, 1)


def decide(items: list[Item], values: dict[str, str]) -> dict:
    case = axis_score(items, values, "case")
    ability = axis_score(items, values, "ability")
    gates_hit = [i for i in items if i.kind == "gate" and values[i.id] == "yes"]
    defer = [g for g in gates_hit if g.effect == "defer"]
    cap = [g for g in gates_hit if g.effect == "cap_partial"]
    reasons: list[str] = []
    if defer:
        outcome = "DEFER"
        reasons.append("Gate answered yes with effect defer: " + "; ".join(f"{g.id} {g.name}" for g in defer)
                       + ". Resolve it, then score again.")
    elif case >= CASE_CONSOLIDATE and ability >= ABILITY_CONSOLIDATE:
        outcome = "CONSOLIDATE"
        reasons.append(f"Case {case} is at least {CASE_CONSOLIDATE:g} and ability to deliver {ability} is at least {ABILITY_CONSOLIDATE:g}.")
    elif case >= CASE_PARTIAL:
        outcome = "PARTIALLY INTEGRATE"
        if case >= CASE_CONSOLIDATE:
            reasons.append(f"The case is strong ({case}) but ability to deliver is {ability}, below {ABILITY_CONSOLIDATE:g}. "
                           "Partial integration lowers the risk and prepares the ground. Revisit after the weakest criteria improve.")
        else:
            reasons.append(f"Case {case} is between {CASE_PARTIAL:g} and {CASE_CONSOLIDATE:g}: some shared benefit, not enough to justify a full migration.")
    else:
        outcome = "KEEP SEPARATE"
        reasons.append(f"Case {case} is below {CASE_PARTIAL:g}: the benefit of a single platform does not outweigh the cost and risk.")
    if cap and outcome == "CONSOLIDATE":
        outcome = "PARTIALLY INTEGRATE"
        reasons.append("Capped by gate(s): " + "; ".join(f"{g.id} {g.name}" for g in cap) + ".")
    elif cap:
        reasons.append("Gate(s) answered yes, which would cap the outcome at partial integration: " + "; ".join(g.id for g in cap) + ".")
    return {"outcome": outcome, "case_score": case, "ability_score": ability, "reasons": reasons,
            "gates_hit": [g.id for g in gates_hit]}


def sensitivity(items: list[Item], values: dict[str, str], base_outcome: str) -> list[dict]:
    """Criteria where moving one score by one point changes the outcome."""
    flips = []
    for item in items:
        if item.kind != "criterion":
            continue
        current = int(values[item.id])
        for delta in (-1, 1):
            new = current + delta
            if not 1 <= new <= 5:
                continue
            trial = dict(values)
            trial[item.id] = str(new)
            result = decide(items, trial)["outcome"]
            if result != base_outcome:
                flips.append({"id": item.id, "name": item.name, "from": current, "to": new, "outcome": result})
    return flips


def full_result(items: list[Item], values: dict[str, str], evidence: dict[str, str], warnings: list[str]) -> dict:
    res = decide(items, values)
    res["kind"] = "decision"
    res["sensitivity"] = sensitivity(items, values, res["outcome"])
    weak = [i for i in items if i.kind == "criterion" and int(values[i.id]) <= 2]
    res["weak_criteria"] = [{"id": i.id, "name": i.name, "axis": i.axis, "score": int(values[i.id])}
                            for i in sorted(weak, key=lambda i: (-i.weight, i.id))]
    res["warnings"] = warnings
    res["scores"] = [{"id": i.id, "name": i.name, "kind": i.kind, "axis": i.axis, "weight": i.weight,
                      "value": values[i.id], "evidence": evidence.get(i.id, "")} for i in items]
    return res


def render_markdown(name: str, res: dict) -> str:
    lines = [f"# Consolidation decision: {name}", "", f"**Outcome: {res['outcome']}**", ""]
    lines += [f"- Case for consolidation: {res['case_score']} out of 100 (consolidate needs {CASE_CONSOLIDATE:g} or more)",
              f"- Ability to deliver: {res['ability_score']} out of 100 (consolidate needs {ABILITY_CONSOLIDATE:g} or more)"]
    lines += [f"- {r}" for r in res["reasons"]]
    lines += ["", "This is a structured prompt for a decision meeting. The scores are only as good as the evidence "
              "behind them, and a different panel could score differently.", ""]
    for kind, axis, title in (("criterion", "case", "Case for consolidation"), ("criterion", "ability", "Ability to deliver")):
        rows = [s for s in res["scores"] if s["kind"] == kind and s["axis"] == axis]
        lines += [f"## {title}", "", "| Id | Criterion | Weight | Score | Evidence |", "|---|---|---:|---:|---|"]
        lines += [f"| {s['id']} | {s['name']} | {s['weight']} | {s['value']} | {s['evidence']} |" for s in rows]
        lines.append("")
    lines += ["## Gates", "", "| Id | Gate | Answer | Evidence |", "|---|---|---|---|"]
    lines += [f"| {s['id']} | {s['name']} | {s['value']} | {s['evidence']} |" for s in res["scores"] if s["kind"] == "gate"]
    lines += ["", "## Weakest criteria (scored 1 or 2)", ""]
    lines += [f"- {w['id']} {w['name']} ({w['axis']}): {w['score']}" for w in res["weak_criteria"]] or ["None."]
    lines += ["", "## Sensitivity: one point can change the outcome", ""]
    lines += [f"- {f['id']} {f['name']}: {f['from']} to {f['to']} gives {f['outcome']}" for f in res["sensitivity"]] or [
        "No single criterion moved by one point changes the outcome."]
    if res["warnings"]:
        lines += ["", "## Warnings", ""] + [f"- {w}" for w in res["warnings"]]
    return "\n".join(lines)
