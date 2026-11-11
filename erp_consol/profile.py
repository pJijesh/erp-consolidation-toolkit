"""Data quality profile of one extract."""

from __future__ import annotations

import os
from collections import Counter
from dataclasses import dataclass

from .csvio import Table
from .errors import InputError
from .normalise import (
    DEFAULT_DATE_FORMATS,
    POSTCODE_PATTERNS,
    TAX_PATTERNS,
    is_placeholder,
    matching_date_format,
    normalise_country,
    valid_email,
    valid_postcode,
    valid_tax,
)

import re

CHECK_TYPES = ("postcode", "tax", "email", "date", "number", "regex")
MAX_EXAMPLES = 5


@dataclass(frozen=True)
class Check:
    column: str
    type: str
    arg: str = ""  # country code, date formats separated by |, or a regular expression

    def describe(self) -> str:
        return self.type + (f":{self.arg}" if self.arg else "")


def parse_check(spec: str) -> Check:
    """Parse 'column=type' or 'column=type:argument'.

    Examples: postcode=postcode, vat_no=tax:GB, created=date:%d/%m/%Y|%Y-%m-%d, ref=regex:^[A-Z]{3}[0-9]+$
    """
    if "=" not in spec:
        raise InputError(f"--check '{spec}' should look like column=type, for example postcode=postcode.")
    column, rest = spec.split("=", 1)
    column = column.strip()
    ctype, _, arg = rest.partition(":")
    ctype = ctype.strip().lower()
    if ctype not in CHECK_TYPES:
        raise InputError(f"--check '{spec}': unknown type '{ctype}'. Types: {', '.join(CHECK_TYPES)}.")
    if ctype == "regex":
        if not arg:
            raise InputError(f"--check '{spec}': regex needs a pattern after the colon.")
        try:
            re.compile(arg)
        except re.error as exc:
            raise InputError(f"--check '{spec}': invalid regular expression: {exc}") from exc
    if ctype in ("postcode", "tax") and arg:
        table = POSTCODE_PATTERNS if ctype == "postcode" else TAX_PATTERNS
        if arg.upper() not in table:
            raise InputError(
                f"--check '{spec}': no {ctype} pattern for '{arg}'. Available: {', '.join(sorted(table))}."
            )
        arg = arg.upper()
    return Check(column, ctype, arg)


def _truncate(value: str, n: int = 40) -> str:
    value = value.replace("\n", " ")
    return value if len(value) <= n else value[: n - 3] + "..."


def _check_value(check: Check, value: str, country: str | None, formats: list[str]) -> tuple[bool, str | None]:
    """Return (is_valid, date_format_used)."""
    if check.type == "postcode":
        return valid_postcode(value, check.arg or country), None
    if check.type == "tax":
        return valid_tax(value, check.arg or country), None
    if check.type == "email":
        return valid_email(value), None
    if check.type == "date":
        fmt = matching_date_format(value, formats)
        return fmt is not None, fmt
    if check.type == "number":
        try:
            float(value.replace(",", ""))
            return True, None
        except ValueError:
            return False, None
    return bool(re.search(check.arg, value)), None


def profile_table(
    table: Table,
    *,
    key: str | None = None,
    required: list[str] | None = None,
    checks: list[Check] | None = None,
    country_col: str | None = None,
    include_examples: bool = True,
) -> dict:
    """Profile a table and return a JSON-ready dictionary. The input is never modified."""
    required = required or []
    checks = checks or []
    wanted = [c for c in ([key] if key else []) + required + [c.column for c in checks] + ([country_col] if country_col else [])]
    real = table.resolve(sorted(set(wanted)))
    n = len(table.rows)
    check_by_col: dict[str, list[Check]] = {}
    for c in checks:
        check_by_col.setdefault(real[c.column], []).append(c)

    columns_out = []
    total_checked = 0
    total_invalid = 0
    for col in table.columns:
        values = [r[col] for r in table.rows]
        blank = sum(1 for v in values if v.strip() == "")
        placeholder = sum(1 for v in values if v.strip() != "" and is_placeholder(v))
        missing = blank + placeholder
        present = [v for v in values if v.strip() != "" and not is_placeholder(v)]
        spaces = sum(1 for v in present if v != v.strip() or "  " in v)
        entry = {
            "column": col,
            "blank": blank,
            "placeholder": placeholder,
            "missing": missing,
            "missing_rate": round(missing / n, 4),
            "distinct": len({v.strip() for v in present}),
            "stray_whitespace": spaces,
            "required": any(real.get(r) == col for r in required),
            "checks": [],
        }
        for chk in check_by_col.get(col, []):
            country_values = (
                [r[real[country_col]] for r in table.rows] if country_col else [None] * n
            )
            invalid_values: list[str] = []
            valid = 0
            fmt_counts: Counter[str] = Counter()
            formats = chk.arg.split("|") if (chk.type == "date" and chk.arg) else DEFAULT_DATE_FORMATS
            for row_value, ctry in zip(values, country_values):
                if row_value.strip() == "" or is_placeholder(row_value):
                    continue
                ok, fmt = _check_value(chk, row_value, ctry, formats)
                if ok:
                    valid += 1
                    if fmt:
                        fmt_counts[fmt] += 1
                else:
                    invalid_values.append(row_value)
            checked = valid + len(invalid_values)
            total_checked += checked
            total_invalid += len(invalid_values)
            result = {
                "check": chk.describe(),
                "checked": checked,
                "valid": valid,
                "invalid": len(invalid_values),
                "invalid_rate": round(len(invalid_values) / checked, 4) if checked else 0.0,
            }
            if chk.type == "date":
                result["formats_seen"] = dict(sorted(fmt_counts.items()))
                result["mixed_formats"] = len(fmt_counts) > 1
            if include_examples:
                result["invalid_examples"] = [_truncate(v) for v in sorted(set(invalid_values))[:MAX_EXAMPLES]]
            entry["checks"].append(result)
        columns_out.append(entry)

    key_info = None
    key_dup_rows = 0
    if key:
        kcol = real[key]
        counts = Counter(r[kcol].strip() for r in table.rows)
        dup_values = sorted(v for v, c in counts.items() if c > 1 and v != "")
        key_dup_rows = sum(counts[v] for v in dup_values)
        blank_keys = counts.get("", 0)
        key_info = {
            "column": kcol,
            "duplicate_values": len(dup_values),
            "rows_with_duplicate_key": key_dup_rows,
            "blank_keys": blank_keys,
        }
        if include_examples:
            key_info["examples"] = [_truncate(v) for v in dup_values[:MAX_EXAMPLES]]

    row_counts = Counter(tuple(r[c] for c in table.columns) for r in table.rows)
    identical_rows = sum(c - 1 for c in row_counts.values() if c > 1)

    required_rates = [e["missing_rate"] for e in columns_out if e["required"]]
    summary = {
        "kind": "profile",
        "dataset": os.path.basename(table.path),
        "rows": n,
        "columns": len(table.columns),
        "required_columns": sorted(real[r] for r in required),
        "required_max_missing_rate": max(required_rates) if required_rates else None,
        "key_column": real[key] if key else None,
        "key_duplicate_rate": round(key_dup_rows / n, 4) if key else None,
        "format_checked_values": total_checked,
        "format_invalid_values": total_invalid,
        "format_invalid_rate": round(total_invalid / total_checked, 4) if total_checked else None,
        "identical_rows": identical_rows,
        "encoding": table.encoding,
        "warnings": list(table.warnings),
        "column_detail": columns_out,
        "key": key_info,
    }
    return summary


def _cell(text: str) -> str:
    """Escape pipe characters so a value cannot break a Markdown table row."""
    return text.replace("|", "\\|")


def _pct(x: float | None) -> str:
    return "n/a" if x is None else f"{x * 100:.1f}%"


def render_markdown(profile: dict) -> str:
    lines = [f"# Data profile: {profile['dataset']}", ""]
    lines += [
        f"- Rows: {profile['rows']}",
        f"- Columns: {profile['columns']}",
        f"- Encoding read as: {profile['encoding']}",
    ]
    if profile["key_column"]:
        k = profile["key"]
        lines.append(
            f"- Key column `{k['column']}`: {k['duplicate_values']} duplicated value(s) covering "
            f"{k['rows_with_duplicate_key']} row(s) ({_pct(profile['key_duplicate_rate'])}), {k['blank_keys']} blank key(s)"
        )
    lines.append(f"- Fully identical rows beyond the first: {profile['identical_rows']}")
    if profile["required_max_missing_rate"] is not None:
        lines.append(f"- Highest missing rate among required columns: {_pct(profile['required_max_missing_rate'])}")
    if profile["format_invalid_rate"] is not None:
        lines.append(
            f"- Format checks: {profile['format_invalid_values']} invalid of {profile['format_checked_values']} "
            f"checked values ({_pct(profile['format_invalid_rate'])})"
        )
    for w in profile["warnings"]:
        lines.append(f"- Warning: {w}")
    lines += ["", "## Columns", "", "| Column | Required | Missing | Missing rate | Distinct | Stray spaces |", "|---|---|---:|---:|---:|---:|"]
    for c in profile["column_detail"]:
        lines.append(
            f"| {c['column']} | {'yes' if c['required'] else ''} | {c['missing']} | {_pct(c['missing_rate'])} | "
            f"{c['distinct']} | {c['stray_whitespace']} |"
        )
    any_checks = [c for c in profile["column_detail"] if c["checks"]]
    if any_checks:
        lines += ["", "## Format checks", "", "| Column | Check | Checked | Invalid | Invalid rate | Examples of invalid values |", "|---|---|---:|---:|---:|---|"]
        for c in any_checks:
            for chk in c["checks"]:
                ex = _cell("; ".join(f"`{e}`" for e in chk.get("invalid_examples", [])))
                lines.append(
                    f"| {c['column']} | {_cell(chk['check'])} | {chk['checked']} | {chk['invalid']} | {_pct(chk['invalid_rate'])} | {ex} |"
                )
                if chk.get("mixed_formats"):
                    seen = _cell(", ".join(f"`{k}` x {v}" for k, v in chk["formats_seen"].items()))
                    lines.append(f"| | mixed date formats | | | | {seen} |")
    if profile["key"] and profile["key"].get("examples"):
        lines += ["", "## Duplicate key values", ""]
        lines += [f"- `{e}`" for e in profile["key"]["examples"]]
    lines += [
        "",
        "Missing means blank or a placeholder such as TBC, N/A or a lone dash. "
        "Format checks test the shape of a value only. They do not prove that a postcode, tax number or "
        "address exists.",
    ]
    return "\n".join(lines)
