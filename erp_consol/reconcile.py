"""Compare trial balances before and after applying a chart of accounts mapping."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal

from .coa import Account
from .csvio import Table
from .errors import InputError
from .normalise import normalise_account_code, parse_amount

ZERO = Decimal("0")
CLASSES = ("asset", "liability", "equity", "revenue", "expense", "unclassified")
TB_COLUMNS = {"period": "period", "account": "account", "debit": "debit", "credit": "credit", "balance": "balance"}


@dataclass
class TrialBalance:
    name: str
    net: dict[tuple[str, str], Decimal]  # (period, account) -> debit minus credit
    periods: list[str]
    warnings: list[str]


def load_trial_balance(table: Table, overrides: dict[str, str] | None = None, decimal_comma: bool = False) -> TrialBalance:
    """Read a trial balance with period and account plus either debit and credit, or a signed balance.

    The sign convention is debit positive, credit negative.
    """
    names = {k: (overrides or {}).get(k, v) for k, v in TB_COLUMNS.items()}
    real = table.resolve([names["period"], names["account"]])
    debit = table.find_column(names["debit"])
    credit = table.find_column(names["credit"])
    balance = table.find_column(names["balance"])
    if not debit and not credit and not balance:
        raise InputError(
            f"{table.name}: needs either 'debit' and 'credit' columns, or a signed 'balance' column. "
            f"Columns found: {', '.join(table.columns)}. Use --tb-map to name them."
        )
    net: dict[tuple[str, str], Decimal] = defaultdict(lambda: ZERO)
    problems: list[str] = []
    repeated = 0
    seen: set[tuple[str, str]] = set()
    for row, line in zip(table.rows, table.lines):
        period = row[real[names["period"]]].strip()
        account = normalise_account_code(row[real[names["account"]]])
        if not period or not account:
            problems.append(f"line {line}: blank period or account")
            continue
        try:
            if debit or credit:
                value = (parse_amount(row[debit], decimal_comma) if debit else ZERO) - (
                    parse_amount(row[credit], decimal_comma) if credit else ZERO)
            else:
                value = parse_amount(row[balance], decimal_comma)
        except InputError as exc:
            problems.append(f"line {line}: {exc}")
            continue
        if (period, account) in seen:
            repeated += 1
        seen.add((period, account))
        net[(period, account)] += value
    if problems:
        shown = "; ".join(problems[:5]) + (f"; and {len(problems) - 5} more" if len(problems) > 5 else "")
        raise InputError(f"{table.name}: cannot read the trial balance: {shown}")
    warnings = []
    if repeated:
        warnings.append(f"{repeated} repeated period and account line(s) in {table.name} were added together.")
    periods = sorted({p for p, _ in net})
    return TrialBalance(table.name, dict(net), periods, warnings)


def balance_accounts(tb: TrialBalance) -> set[str]:
    return {a for (_, a), v in tb.net.items() if v != ZERO}


def _cls(acc: Account | None) -> str:
    return acc.type if acc and acc.type else "unclassified"


def _q(x: Decimal) -> str:
    return f"{x.quantize(Decimal('0.01')):.2f}"


def reconcile(
    tb: TrialBalance,
    mapping: dict[str, str],
    source_chart: list[Account],
    target_chart: list[Account],
    tolerance: Decimal,
    target_tb: TrialBalance | None = None,
    allow_reclassification: bool = False,
) -> tuple[dict, list[list[object]]]:
    src = {a.code: a for a in source_chart}
    tgt = {a.code: a for a in target_chart}
    warnings = list(tb.warnings) + (list(target_tb.warnings) if target_tb else [])
    unknown_accounts = sorted({a for (_, a) in tb.net if a not in src})
    if unknown_accounts:
        warnings.append(
            f"{len(unknown_accounts)} account(s) in the trial balance are not in the source chart and are treated as "
            f"unclassified: {', '.join(unknown_accounts[:5])}{' ...' if len(unknown_accounts) > 5 else ''}."
        )
    bad_targets = sorted({t for t in mapping.values() if t not in tgt})
    if bad_targets:
        raise InputError(
            f"The mapping points to {len(bad_targets)} account(s) that are not in the target chart: "
            f"{', '.join(bad_targets[:5])}{' ...' if len(bad_targets) > 5 else ''}."
        )

    period_rows, diff_rows = [], []
    unmapped_accounts_seen: set[str] = set()
    target_tb_diffs = 0
    max_abs = ZERO

    for period in tb.periods:
        lines = {a: v for (p, a), v in tb.net.items() if p == period}
        debit = sum((v for v in lines.values() if v > ZERO), ZERO)
        credit = -sum((v for v in lines.values() if v < ZERO), ZERO)
        src_net = sum(lines.values(), ZERO)
        mapped_net = sum((v for a, v in lines.items() if a in mapping), ZERO)
        unmapped = {a: v for a, v in lines.items() if a not in mapping}
        unmapped_net = sum(unmapped.values(), ZERO)

        before = defaultdict(lambda: ZERO)
        after = defaultdict(lambda: ZERO)
        unmapped_by_class = defaultdict(lambda: ZERO)
        for a, v in lines.items():
            before[_cls(src.get(a))] += v
            if a in mapping:
                after[_cls(tgt[mapping[a]])] += v
            else:
                unmapped_by_class[_cls(src.get(a))] += v
        reclass = {c: after[c] - (before[c] - unmapped_by_class[c]) for c in CLASSES}
        flags: list[str] = []

        if abs(src_net) > tolerance:
            flags.append("source_out_of_balance")
            diff_rows.append(["source_out_of_balance", period, "", _q(ZERO), _q(src_net), _q(src_net), "source trial balance does not net to zero"])
            max_abs = max(max_abs, abs(src_net))
        for a, v in sorted(unmapped.items()):
            if abs(v) > tolerance:
                unmapped_accounts_seen.add(a)
                flags.append("unmapped_balance")
                diff_rows.append(["unmapped_balance", period, a, _q(v), _q(ZERO), _q(-v), f"{src[a].name if a in src else 'account not in source chart'}: balance has no approved mapping"])
                max_abs = max(max_abs, abs(v))
        for c in CLASSES:
            if abs(reclass[c]) > tolerance:
                if not allow_reclassification:
                    flags.append("reclassification")
                diff_rows.append(["reclassification_accepted" if allow_reclassification else "reclassification", period, c, _q(before[c] - unmapped_by_class[c]), _q(after[c]), _q(reclass[c]),
                                  "balances moved between classes because source and target account types differ"])
                max_abs = max(max_abs, abs(reclass[c]))

        tb_diff_count: int | str = ""
        if target_tb is not None:
            expected: dict[str, Decimal] = defaultdict(lambda: ZERO)
            for a, v in lines.items():
                if a in mapping:
                    expected[mapping[a]] += v
            actual = {a: v for (p, a), v in target_tb.net.items() if p == period}
            tb_diff_count = 0
            for a in sorted(set(expected) | set(actual)):
                e, ac = expected.get(a, ZERO), actual.get(a, ZERO)
                d = ac - e
                if abs(d) > tolerance:
                    tb_diff_count += 1
                    target_tb_diffs += 1
                    max_abs = max(max_abs, abs(d))
                    diff_rows.append(["target_tb_difference", period, a, _q(e), _q(ac), _q(d),
                                      f"{tgt[a].name if a in tgt else 'account not in target chart'}: loaded balance differs from the mapped source"])
            if tb_diff_count:
                flags.append("target_tb_difference")
            if target_tb is not None and period not in target_tb.periods:
                flags.append("period_missing_in_target_tb")
                diff_rows.append(["period_missing_in_target_tb", period, "", "", "", "", "no rows for this period in the target trial balance"])

        period_rows.append({
            "period": period, "source_debit": _q(debit), "source_credit": _q(credit), "source_net": _q(src_net),
            "mapped_net": _q(mapped_net), "unmapped_net": _q(unmapped_net),
            "unmapped_accounts_with_balance": sum(1 for v in unmapped.values() if abs(v) > tolerance),
            "reclassified_abs": _q(sum((abs(reclass[c]) for c in CLASSES), ZERO) / 2),
            "target_tb_differences": tb_diff_count,
            "status": "OK" if not flags else "DIFFERENCES",
            "flags": ";".join(sorted(set(flags))),
            "class_detail": {c: {"before": _q(before[c]), "unmapped": _q(unmapped_by_class[c]), "after": _q(after[c]), "reclassified": _q(reclass[c])} for c in CLASSES},
        })

    n_ok = sum(1 for r in period_rows if r["status"] == "OK")
    summary = {
        "kind": "reconcile",
        "periods": len(period_rows),
        "periods_ok": n_ok,
        "periods_with_differences": len(period_rows) - n_ok,
        "tolerance": str(tolerance),
        "unmapped_accounts_with_balance": len(unmapped_accounts_seen),
        "reclassification_accepted": allow_reclassification,
        "target_tb_compared": target_tb is not None,
        "target_tb_differences": target_tb_diffs,
        "largest_absolute_difference": _q(max_abs),
        "warnings": warnings,
        "periods_detail": period_rows,
    }
    return summary, diff_rows


PERIOD_HEADER = [
    "period", "source_debit", "source_credit", "source_net", "mapped_net", "unmapped_net",
    "unmapped_accounts_with_balance", "reclassified_abs", "target_tb_differences", "status", "flags",
]
DIFF_HEADER = ["type", "period", "account_or_class", "expected_or_before", "actual_or_after", "difference", "note"]


def period_csv_rows(summary: dict) -> list[list[object]]:
    return [[r[h] for h in PERIOD_HEADER] for r in summary["periods_detail"]]


def render_markdown(name: str, summary: dict, diff_rows: list[list[object]], limit: int = 40) -> str:
    s = summary
    lines = [f"# Trial balance reconciliation: {name}", ""]
    lines += [
        f"- Periods: {s['periods']}; clean: {s['periods_ok']}; with differences: {s['periods_with_differences']}",
        f"- Tolerance: {s['tolerance']} (absolute, per account and per class)",
        f"- Source accounts with a balance but no approved mapping: {s['unmapped_accounts_with_balance']}",
        f"- Largest absolute difference found: {s['largest_absolute_difference']}",
    ]
    if s["target_tb_compared"]:
        lines.append(f"- Loaded target trial balance compared: {s['target_tb_differences']} account and period difference(s) beyond tolerance")
    for w in s["warnings"]:
        lines.append(f"- Warning: {w}")
    lines += ["", "Amounts are debit positive and credit negative, in the currency of the trial balance. "
              "No currency translation is done.", "", "## By period", "",
              "| Period | Source debit | Source credit | Source net | Mapped net | Unmapped net | Unmapped accounts | Status |",
              "|---|---:|---:|---:|---:|---:|---:|---|"]
    for r in s["periods_detail"]:
        lines.append(f"| {r['period']} | {r['source_debit']} | {r['source_credit']} | {r['source_net']} | {r['mapped_net']} | "
                     f"{r['unmapped_net']} | {r['unmapped_accounts_with_balance']} | {r['status']} |")
    last = s["periods_detail"][-1] if s["periods_detail"] else None
    if last:
        lines += ["", f"## Balances by account class, latest period ({last['period']})", "",
                  "| Class | Before (source type) | Unmapped | After (target type) | Reclassified |", "|---|---:|---:|---:|---:|"]
        for c in CLASSES:
            d = last["class_detail"][c]
            if all(Decimal(d[k]) == ZERO for k in d):
                continue
            lines.append(f"| {c} | {d['before']} | {d['unmapped']} | {d['after']} | {d['reclassified']} |")
        lines.append("\nReclassified is the movement between classes that the mapping itself causes, "
                     "separate from balances left out because they are unmapped.")
    lines += ["", f"## Differences beyond tolerance ({len(diff_rows)})", ""]
    if diff_rows:
        lines += ["| Type | Period | Account or class | Expected or before | Actual or after | Difference | Note |", "|---|---|---|---:|---:|---:|---|"]
        for r in diff_rows[:limit]:
            lines.append("| " + " | ".join(str(x) for x in r) + " |")
        if len(diff_rows) > limit:
            lines.append(f"\nThe first {limit} are shown. The full list is in the differences CSV.")
    else:
        lines.append("None.")
    return "\n".join(lines)
