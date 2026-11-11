"""Map a source chart of accounts to a target chart.

Order of precedence:
1. A manual mapping file. These rows are treated as approved.
2. Suggestions from account type and normalised name similarity. These are never
   approved by the tool: a person copies the ones they accept into the manual file.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .csvio import Table, read_table
from .errors import InputError
from .normalise import fold_text, normalise_account_code, similarity

ACCOUNT_TYPES = ("asset", "liability", "equity", "revenue", "expense")

# Words that identify a type inside a free-text type label. Order matters: the first
# group with a hit wins, so "Cost of Sales" is an expense and not revenue.
_TYPE_KEYWORDS = [
    ("expense", {"expense", "expenses", "cost", "costs", "overhead", "overheads", "cogs", "expenditure", "depreciation"}),
    ("liability", {"liability", "liabilities", "payable", "payables", "creditor", "creditors", "accrual", "accruals", "loan", "loans"}),
    ("equity", {"equity", "capital", "reserve", "reserves", "retained"}),
    ("asset", {"asset", "assets", "bank", "cash", "receivable", "receivables", "debtor", "debtors", "inventory", "stock", "prepayment", "prepayments"}),
    ("revenue", {"revenue", "revenues", "income", "sales", "turnover"}),
]

# Words that differ between charts but mean the same thing. Applied to both sides.
ACCOUNT_SYNONYMS = {
    "debtors": "receivables", "debtor": "receivables", "creditors": "payables", "creditor": "payables",
    "stock": "inventory", "stocks": "inventory", "sales": "revenue", "turnover": "revenue",
    "acc": "accumulated", "accum": "accumulated", "depn": "depreciation", "dep": "depreciation",
    "lt": "long term", "hp": "hire purchase", "ni": "national insurance",
    "ppv": "purchase price variance", "grni": "goods received not invoiced",
    "wip": "work in progress", "prov": "provision", "tel": "telephone", "equip": "equipment",
    "mgmt": "management",
}
_COMPOUND_ABBREVIATIONS = {
    "p&m": "plant and machinery", "f&f": "fixtures and fittings", "r&m": "repairs and maintenance",
    "m/v": "motor vehicles", "i/c": "intercompany",
}
_FILLER = {"account", "a/c", "ac", "the", "of", "and", "for", "to", "in"}


def normalise_type(label: str | None, extra: dict[str, str] | None = None) -> str:
    """Return one of ACCOUNT_TYPES, or an empty string when the label is not recognised."""
    if not label or not label.strip():
        return ""
    key = fold_text(label).strip()
    if extra and key in extra:
        return extra[key]
    if key in ACCOUNT_TYPES:
        return key
    words = set(re.sub(r"[^a-z]+", " ", key).split())
    for atype, vocab in _TYPE_KEYWORDS:
        if words & vocab:
            return atype
    return ""


def normalise_account_name(name: str) -> str:
    text = fold_text(name or "")
    for abbr, full in _COMPOUND_ABBREVIATIONS.items():
        text = text.replace(abbr, full)
    text = text.replace("&", " and ")
    words = re.sub(r"[^a-z0-9]+", " ", text).split()
    out: list[str] = []
    for w in words:
        out.extend(ACCOUNT_SYNONYMS.get(w, w).split())
    out = [w for w in out if w not in _FILLER] or out
    return " ".join(out)


@dataclass
class Account:
    code: str
    name: str
    type_label: str
    type: str
    postable: bool
    norm_name: str
    line: int


def _truthy(value: str) -> bool:
    return value.strip().lower() not in ("n", "no", "false", "0", "f")


def load_chart(table: Table, cols: dict[str, str], extra_types: dict[str, str] | None = None) -> list[Account]:
    """Turn a Table into Accounts. `cols` maps account, name, type, postable to real headers."""
    wanted = [cols.get("account", "account"), cols.get("name", "name")]
    real = table.resolve(wanted)
    code_col, name_col = real[wanted[0]], real[wanted[1]]
    type_col = table.find_column(cols.get("type", "type"))
    post_col = table.find_column(cols.get("postable", "postable"))
    seen: dict[str, int] = {}
    accounts: list[Account] = []
    problems: list[str] = []
    for row, line in zip(table.rows, table.lines):
        code = normalise_account_code(row[code_col])
        name = row[name_col].strip()
        if not code or not name:
            problems.append(f"line {line}: account code or name is blank")
            continue
        if code in seen:
            problems.append(f"line {line}: account '{code}' already appears on line {seen[code]}")
            continue
        seen[code] = line
        label = row[type_col].strip() if type_col else ""
        accounts.append(
            Account(
                code, name, label, normalise_type(label, extra_types),
                _truthy(row[post_col]) if post_col and row[post_col].strip() else True,
                normalise_account_name(name), line,
            )
        )
    if problems:
        shown = "; ".join(problems[:5]) + (f"; and {len(problems) - 5} more" if len(problems) > 5 else "")
        raise InputError(f"{table.name}: invalid chart of accounts: {shown}.")
    return accounts


def load_manual_mapping(path: str) -> list[tuple[str, str, int]]:
    """Read source_account, target_account pairs. A header-only file means no manual mappings."""
    table = read_table(path, allow_empty=True)
    real = table.resolve(["source_account", "target_account"])
    out = []
    for row, line in zip(table.rows, table.lines):
        src = normalise_account_code(row[real["source_account"]])
        tgt = normalise_account_code(row[real["target_account"]])
        if not src or not tgt:
            raise InputError(f"{table.name}: line {line} has a blank source_account or target_account.")
        out.append((src, tgt, line))
    return out


def load_mapping_for_use(path: str, include_suggested: bool = False) -> tuple[dict[str, str], list[str]]:
    """Read a mapping file for reconcile. Works for map-coa output and for a plain manual file."""
    table = read_table(path)
    real = table.resolve(["source_account", "target_account"])
    status_col = table.find_column("status")
    mapping: dict[str, str] = {}
    notes: list[str] = []
    skipped = 0
    for row, line in zip(table.rows, table.lines):
        src = normalise_account_code(row[real["source_account"]])
        tgt = normalise_account_code(row[real["target_account"]])
        if not tgt:
            skipped += 1
            continue
        if status_col:
            status = row[status_col].strip().lower()
            allowed = {"approved", "review"} if include_suggested else {"approved"}
            if status not in allowed:
                skipped += 1
                continue
        if src in mapping and mapping[src] != tgt:
            raise InputError(f"{table.name}: line {line}: source account '{src}' is mapped to two different targets.")
        mapping[src] = tgt
    if skipped:
        what = "unmapped or unapproved" if status_col else "unmapped"
        notes.append(f"{skipped} {what} row(s) in {table.name} were not used.")
    return mapping, notes


def _best_candidates(src: Account, targets: list[Account]) -> list[tuple[float, Account]]:
    pool = [t for t in targets if t.postable and (not src.type or t.type == src.type)]
    scored = [(similarity(src.norm_name, t.norm_name), t) for t in pool]
    scored.sort(key=lambda p: (-p[0], p[1].code))
    return scored


def map_chart(
    source: list[Account],
    target: list[Account],
    manual: list[tuple[str, str, int]],
    *,
    balance_accounts: set[str] | None = None,
    high: float = 0.85,
    low: float = 0.65,
    ambiguity_margin: float = 0.03,
) -> tuple[list[dict], list[dict], dict]:
    """Return (mapping rows, exception rows, summary)."""
    src_by_code = {a.code: a for a in source}
    tgt_by_code = {a.code: a for a in target}
    exceptions: list[dict] = []

    def add(severity: str, account: str, issue: str, detail: str) -> None:
        exceptions.append({"severity": severity, "source_account": account, "issue": issue, "detail": detail})

    manual_map: dict[str, str] = {}
    for src_code, tgt_code, line in manual:
        if src_code not in src_by_code:
            add("warning", src_code, "manual_source_unknown", f"manual mapping line {line} names a source account that is not in the source chart")
            continue
        if src_code in manual_map and manual_map[src_code] != tgt_code:
            add("error", src_code, "manual_conflict", f"mapped to both {manual_map[src_code]} and {tgt_code} in the manual file")
            continue
        manual_map[src_code] = tgt_code

    rows: list[dict] = []
    for acc in source:
        has_bal = None if balance_accounts is None else acc.code in balance_accounts
        row = {
            "source_account": acc.code, "source_name": acc.name, "source_type": acc.type or acc.type_label,
            "target_account": "", "target_name": "", "method": "none", "confidence": "",
            "status": "unmapped", "flags": [], "has_balance": has_bal,
        }
        if not acc.type:
            row["flags"].append("type_unknown")
            add("warning", acc.code, "type_unknown", f"source type '{acc.type_label}' is not recognised, so type checks and type-limited suggestions cannot be applied")
        if acc.code in manual_map:
            tgt = tgt_by_code.get(manual_map[acc.code])
            if tgt is None:
                row["flags"].append("manual_target_unknown")
                add("error", acc.code, "manual_target_unknown", f"manual mapping points to {manual_map[acc.code]}, which is not in the target chart")
            else:
                row.update(target_account=tgt.code, target_name=tgt.name, method="manual", confidence="1.00", status="approved")
                if not tgt.postable:
                    row["flags"].append("target_not_postable")
                    add("warning", acc.code, "target_not_postable", f"target {tgt.code} is not a postable account")
                if acc.type and tgt.type and acc.type != tgt.type:
                    row["flags"].append("type_mismatch")
                    add("warning", acc.code, "type_mismatch", f"source is {acc.type} but target {tgt.code} is {tgt.type}")
        else:
            cands = _best_candidates(acc, target)
            # An account whose type is not recognised is compared with every target type, so a
            # suggestion needs high confidence. A weaker name match would be too easy to rubber-stamp.
            floor = low if acc.type else max(low, high)
            if cands and cands[0][0] >= floor:
                score, tgt = cands[0]
                row.update(target_account=tgt.code, target_name=tgt.name, method="suggested",
                           confidence=f"{score:.2f}", status="review")
                if score < high:
                    row["flags"].append("low_confidence")
                if len(cands) > 1 and cands[0][0] - cands[1][0] <= ambiguity_margin and cands[1][1].code != tgt.code:
                    row["flags"].append("ambiguous")
                    add("warning", acc.code, "ambiguous",
                        f"{tgt.code} {tgt.name} ({cands[0][0]:.2f}) and {cands[1][1].code} {cands[1][1].name} ({cands[1][0]:.2f}) are almost equally close")
            else:
                closest = f" Closest was {cands[0][1].code} {cands[0][1].name} ({cands[0][0]:.2f})." if cands else " No target account of the same type exists."
                sev = "error" if has_bal else "warning"
                add(sev, acc.code, "unmapped", f"no suggestion at or above {floor:.2f}." + closest + (" The account carries a balance." if has_bal else ""))
        rows.append(row)

    by_target: dict[str, list[dict]] = {}
    for r in rows:
        if r["target_account"]:
            by_target.setdefault(r["target_account"], []).append(r)
    many_to_one = 0
    for tcode in sorted(by_target):
        group = by_target[tcode]
        if len(group) < 2:
            continue
        many_to_one += 1
        any_suggested = any(g["method"] == "suggested" for g in group)
        for g in group:
            g["flags"].append("many_to_one")
        sources = ", ".join(g["source_account"] for g in group)
        add("warning" if any_suggested else "info", group[0]["source_account"], "many_to_one",
            f"{len(group)} source accounts ({sources}) map to {tcode} {group[0]['target_name']}"
            + (": check that the suggestions are not all picking the same nearest name" if any_suggested else ": confirm that merging their detail is intended"))

    for r in rows:
        r["flags"] = ";".join(sorted(set(r["flags"])))
    order = {"error": 0, "warning": 1, "info": 2}
    exceptions.sort(key=lambda e: (order[e["severity"]], e["source_account"], e["issue"]))

    n = len(rows)
    approved = sum(1 for r in rows if r["status"] == "approved")
    review = sum(1 for r in rows if r["status"] == "review")
    unmapped = n - approved - review
    summary = {
        "kind": "coa",
        "source_accounts": n,
        "target_accounts": len(target),
        "approved": approved,
        "suggested_for_review": review,
        "suggested_high_confidence": sum(1 for r in rows if r["status"] == "review" and "low_confidence" not in r["flags"]),
        "unmapped": unmapped,
        "approved_coverage": round(approved / n, 4) if n else 0.0,
        "many_to_one_targets": many_to_one,
        "exceptions_error": sum(1 for e in exceptions if e["severity"] == "error"),
        "exceptions_warning": sum(1 for e in exceptions if e["severity"] == "warning"),
        "balance_accounts": None if balance_accounts is None else sum(1 for r in rows if r["has_balance"]),
        "balance_accounts_not_approved": None if balance_accounts is None else sum(
            1 for r in rows if r["has_balance"] and r["status"] != "approved"),
    }
    return rows, exceptions, summary


def render_markdown(name: str, summary: dict, rows: list[dict], exceptions: list[dict], limit: int = 40) -> str:
    s = summary
    pct = lambda x: f"{x * 100:.1f}%"
    lines = [f"# Chart of accounts mapping: {name}", ""]
    lines += [
        f"- Source accounts: {s['source_accounts']}; target accounts: {s['target_accounts']}",
        f"- Approved (manual mapping file): {s['approved']} ({pct(s['approved_coverage'])})",
        f"- Suggested, waiting for review: {s['suggested_for_review']} ({s['suggested_high_confidence']} at high confidence)",
        f"- Unmapped: {s['unmapped']}",
        f"- Targets receiving more than one source account: {s['many_to_one_targets']}",
        f"- Exceptions: {s['exceptions_error']} error, {s['exceptions_warning']} warning",
    ]
    if s["balance_accounts"] is not None:
        lines.append(
            f"- Accounts with a balance in the trial balance: {s['balance_accounts']}, of which not yet approved: {s['balance_accounts_not_approved']}"
        )
    lines += ["", "Suggestions are never approved by the tool. Review each one, then copy the accepted rows "
              "(source_account, target_account) into the manual mapping file and run again.", ""]
    shown = [e for e in exceptions if e["severity"] != "info"]
    lines += [f"## Exceptions needing attention ({len(shown)})", ""]
    if shown:
        lines += ["| Severity | Source account | Issue | Detail |", "|---|---|---|---|"]
        for e in shown[:limit]:
            lines.append(f"| {e['severity']} | {e['source_account']} | {e['issue']} | {e['detail']} |")
        if len(shown) > limit:
            lines.append(f"\nThe first {limit} are shown. The full list is in the exceptions CSV.")
    else:
        lines.append("None.")
    sugg = sorted((r for r in rows if r["status"] == "review"), key=lambda r: (float(r["confidence"]), r["source_account"]))
    lines += ["", f"## Suggestions, lowest confidence first ({len(sugg)})", ""]
    if sugg:
        lines += ["| Source | Source name | Suggested target | Target name | Confidence | Flags |", "|---|---|---|---|---:|---|"]
        for r in sugg[:limit]:
            lines.append(f"| {r['source_account']} | {r['source_name']} | {r['target_account']} | {r['target_name']} | {r['confidence']} | {r['flags']} |")
        if len(sugg) > limit:
            lines.append(f"\nThe first {limit} are shown. The full list is in the mapping CSV.")
    else:
        lines.append("None.")
    return "\n".join(lines)
