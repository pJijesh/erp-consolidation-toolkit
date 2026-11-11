"""Command line interface: python -m erp_consol <command> ..."""

from __future__ import annotations

import argparse
import os
import sys
from decimal import Decimal, InvalidOperation

from . import __version__, coa, dedupe, decision, profile, readiness, reconcile
from .csvio import (
    parse_pairs, read_json, read_table, write_csv, write_json, write_text,
)
from .errors import EXIT_GATE, EXIT_OK, EXIT_USAGE, InputError
from .normalise import normalise_uom


def _stem(path: str) -> str:
    return os.path.splitext(os.path.basename(path))[0]


def _common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--out", default="output", help="folder for output files (default: output)")
    p.add_argument("--name", help="prefix for output files (default: taken from the main input file name)")
    p.add_argument("--encoding", default="auto", help="text encoding of the input files (default: auto, UTF-8 then Windows-1252)")
    p.add_argument("--delimiter", default=None, help="CSV delimiter (default: detected from the header row)")


def _read(args: argparse.Namespace, path: str, **kw):
    return read_table(path, encoding=args.encoding, delimiter=args.delimiter, **kw)


def _emit(paths: list[str]) -> None:
    for p in paths:
        print(f"wrote {p}")


# ---------------------------------------------------------------------------


def cmd_profile(args: argparse.Namespace) -> int:
    config = read_json(args.config) if args.config else {}
    table = _read(args, args.file)
    key = args.key or config.get("key")
    required = [c.strip() for c in (args.required.split(",") if args.required else config.get("required", [])) if c.strip()]
    country_col = args.country_col or config.get("country_column")
    specs = [f"{col}={spec}" for col, spec in sorted(config.get("checks", {}).items())] + list(args.check or [])
    checks = [profile.parse_check(s) for s in specs]
    result = profile.profile_table(table, key=key, required=required, checks=checks,
                                   country_col=country_col, include_examples=not args.no_examples)
    name = args.name or _stem(args.file)
    result["name"] = name
    md = os.path.join(args.out, f"{name}.profile-report.md")
    js = os.path.join(args.out, f"{name}.profile-summary.json")
    write_text(md, profile.render_markdown(result))
    write_json(js, result)
    print(f"{name}: {result['rows']} rows, {result['columns']} columns, "
          f"format invalid rate {result['format_invalid_rate']}, key duplicate rate {result['key_duplicate_rate']}")
    _emit([md, js])
    return EXIT_OK


def _decimal(text: str, label: str) -> Decimal:
    try:
        value = Decimal(text)
    except InvalidOperation:
        raise InputError(f"{label}: '{text}' is not a number.") from None
    if value < 0:
        raise InputError(f"{label} must not be negative.")
    return value


def cmd_map_coa(args: argparse.Namespace) -> int:
    chart_keys = ["account", "name", "type", "postable"]
    src_table = _read(args, args.source)
    tgt_table = _read(args, args.target)
    src_map = parse_pairs(args.source_map, chart_keys, "--source-map")
    tgt_map = parse_pairs(args.target_map, chart_keys, "--target-map")
    source = coa.load_chart(src_table, src_map)
    target = coa.load_chart(tgt_table, tgt_map)
    manual = coa.load_manual_mapping(args.manual) if args.manual else []
    balances = None
    if args.tb:
        tb = reconcile.load_trial_balance(_read(args, args.tb), parse_pairs(args.tb_map, list(reconcile.TB_COLUMNS), "--tb-map"), args.decimal_comma)
        balances = reconcile.balance_accounts(tb)
    if not 0 < args.min_confidence <= args.high_confidence <= 1:
        raise InputError("Confidence limits must satisfy 0 < --min-confidence <= --high-confidence <= 1.")
    rows, exceptions, summary = coa.map_chart(source, target, manual, balance_accounts=balances,
                                              high=args.high_confidence, low=args.min_confidence)
    name = args.name or _stem(args.source)
    summary["name"] = name
    summary["warnings"] = src_table.warnings + tgt_table.warnings
    p = lambda suffix: os.path.join(args.out, f"{name}.{suffix}")
    write_csv(p("mapping.csv"),
              ["source_account", "source_name", "source_type", "target_account", "target_name", "method",
               "confidence", "status", "flags", "has_balance"],
              [[r["source_account"], r["source_name"], r["source_type"], r["target_account"], r["target_name"], r["method"],
                r["confidence"], r["status"], r["flags"], "" if r["has_balance"] is None else ("yes" if r["has_balance"] else "no")]
               for r in rows])
    write_csv(p("exceptions.csv"), ["severity", "source_account", "issue", "detail"],
              [[e["severity"], e["source_account"], e["issue"], e["detail"]] for e in exceptions])
    write_text(p("coa-report.md"), coa.render_markdown(name, summary, rows, exceptions))
    write_json(p("coa-summary.json"), summary)
    print(f"{name}: {summary['source_accounts']} source accounts, {summary['approved']} approved, "
          f"{summary['suggested_for_review']} suggested, {summary['unmapped']} unmapped, "
          f"{summary['exceptions_error']} error and {summary['exceptions_warning']} warning exceptions")
    _emit([p("mapping.csv"), p("exceptions.csv"), p("coa-report.md"), p("coa-summary.json")])
    if args.fail_on_unapproved and summary["approved"] < summary["source_accounts"]:
        return EXIT_GATE
    return EXIT_OK


def _uom_overrides(text: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for part in (text or "").split(","):
        if part.strip():
            if "=" not in part:
                raise InputError(f"--uom-map: '{part}' should look like FROM=TO.")
            a, b = part.split("=", 1)
            out[normalise_uom(a, {})] = normalise_uom(b, {})
    return out


def cmd_dedupe(args: argparse.Namespace) -> int:
    entity = args.entity
    keys = list(dedupe.PARTY_COLUMNS if entity == "party" else dedupe.PART_COLUMNS)
    a_over = parse_pairs(args.a_map, keys, "--a-map")
    b_over = parse_pairs(args.b_map, keys, "--b-map")
    a_table = _read(args, args.a)
    b_table = _read(args, args.b) if args.b else None
    if entity == "party":
        suffixes = frozenset(s.strip().lower() for s in (args.legal_suffixes or "").split(",") if s.strip())
        recs = dedupe.load_parties(a_table, "A", a_over, suffixes)
        if b_table:
            recs += dedupe.load_parties(b_table, "B", b_over or a_over, suffixes)
    else:
        aliases = _uom_overrides(args.uom_map)
        recs = dedupe.load_parts(a_table, "A", a_over, aliases)
        if b_table:
            recs += dedupe.load_parts(b_table, "B", b_over or a_over, aliases)
    pairs = dedupe.find_pairs(recs, entity, args.auto, args.review)
    labels = {"A": args.a_label, "B": args.b_label}
    summary = dedupe.summarise(entity, recs, pairs, labels, args.auto, args.review)
    name = args.name or entity
    summary["name"] = name
    summary["warnings"] = a_table.warnings + (b_table.warnings if b_table else [])
    p = lambda suffix: os.path.join(args.out, f"{name}.{suffix}")
    write_csv(p("matches.csv"), dedupe.MATCH_HEADER, dedupe.match_rows(pairs))
    write_csv(p("merge-proposal.csv"), dedupe.MERGE_HEADER, dedupe.merge_proposal(pairs, entity))
    write_text(p("dedupe-report.md"), dedupe.render_markdown(name, entity, summary, pairs))
    write_json(p("dedupe-summary.json"), summary)
    print(f"{name}: {summary['records']} records, {summary['auto_pairs']} automatic pairs, "
          f"{summary['review_pairs']} for review, {summary['clusters']} proposed merge groups")
    _emit([p("matches.csv"), p("merge-proposal.csv"), p("dedupe-report.md"), p("dedupe-summary.json")])
    return EXIT_OK


def cmd_reconcile(args: argparse.Namespace) -> int:
    chart_keys = ["account", "name", "type", "postable"]
    tb_keys = list(reconcile.TB_COLUMNS)
    tb_map = parse_pairs(args.tb_map, tb_keys, "--tb-map")
    tolerance = _decimal(args.tolerance, "--tolerance")
    source = coa.load_chart(_read(args, args.source_coa), parse_pairs(args.source_map, chart_keys, "--source-map"))
    target = coa.load_chart(_read(args, args.target_coa), parse_pairs(args.target_map, chart_keys, "--target-map"))
    tb = reconcile.load_trial_balance(_read(args, args.tb), tb_map, args.decimal_comma)
    target_tb = None
    if args.target_tb:
        target_tb = reconcile.load_trial_balance(_read(args, args.target_tb), parse_pairs(args.target_tb_map, tb_keys, "--target-tb-map") or tb_map, args.decimal_comma)
    mapping, notes = coa.load_mapping_for_use(args.mapping, args.include_suggested)
    summary, diffs = reconcile.reconcile(tb, mapping, source, target, tolerance, target_tb, args.allow_reclassification)
    summary["warnings"] = notes + summary["warnings"]
    name = args.name or _stem(args.tb)
    summary["name"] = name
    p = lambda suffix: os.path.join(args.out, f"{name}.{suffix}")
    write_csv(p("reconcile-by-period.csv"), reconcile.PERIOD_HEADER, reconcile.period_csv_rows(summary))
    write_csv(p("reconcile-differences.csv"), reconcile.DIFF_HEADER, diffs)
    write_text(p("reconcile-report.md"), reconcile.render_markdown(name, summary, diffs))
    write_json(p("reconcile-summary.json"), summary)
    print(f"{name}: {summary['periods']} periods, {summary['periods_ok']} clean, "
          f"{summary['periods_with_differences']} with differences, largest difference {summary['largest_absolute_difference']}")
    _emit([p("reconcile-by-period.csv"), p("reconcile-differences.csv"), p("reconcile-report.md"), p("reconcile-summary.json")])
    if args.fail_on_difference and summary["periods_with_differences"]:
        return EXIT_GATE
    return EXIT_OK


def cmd_readiness(args: argparse.Namespace) -> int:
    summaries = [read_json(p) for p in args.inputs]
    overrides = read_json(args.thresholds) if args.thresholds else None
    thresholds = readiness.load_thresholds(overrides)
    result = readiness.evaluate(summaries, thresholds)
    name = args.name or "readiness"
    md = os.path.join(args.out, f"{name}-report.md")
    js = os.path.join(args.out, f"{name}-summary.json")
    write_text(md, readiness.render_markdown(result, thresholds))
    write_json(js, result)
    print(f"Verdict: {result['verdict']} ({result['red']} red, {result['amber']} amber, {result['green']} green)")
    _emit([md, js])
    return EXIT_GATE if (args.fail_on_no_go and result["verdict"] == "NO-GO") else EXIT_OK


def cmd_decide(args: argparse.Namespace) -> int:
    items = decision.load_criteria(args.criteria or decision.default_criteria_path())
    values, evidence, warnings = decision.load_scores(args.scores, items)
    result = decision.full_result(items, values, evidence, warnings)
    name = args.name or _stem(args.scores)
    result["name"] = name
    md = os.path.join(args.out, f"{name}.decision-report.md")
    js = os.path.join(args.out, f"{name}.decision-summary.json")
    write_text(md, decision.render_markdown(name, result))
    write_json(js, result)
    print(f"{name}: {result['outcome']} (case {result['case_score']}, ability {result['ability_score']})")
    _emit([md, js])
    return EXIT_OK


# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="erp_consol",
        description="CSV based checks for consolidating ERP and finance systems. "
                    "It reads extracts, never connects to an ERP and never changes source data.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True, metavar="command")

    p = sub.add_parser("profile", help="data quality profile of an extract", description="Profile one CSV extract: row counts, missing values, duplicate keys and format checks.")
    p.add_argument("file")
    p.add_argument("--key", help="column that should be unique")
    p.add_argument("--required", help="comma separated columns that must be filled")
    p.add_argument("--check", action="append", metavar="COL=TYPE[:ARG]",
                   help="format check, repeatable. Types: postcode, tax, email, date, number, regex. "
                        "Examples: postcode=postcode:GB  vat_no=tax:DE  created=date:%%d/%%m/%%Y|%%Y-%%m-%%d")
    p.add_argument("--country-col", help="column holding the country, used to pick postcode and tax patterns per row")
    p.add_argument("--config", help="JSON file with key, required, country_column and checks")
    p.add_argument("--no-examples", action="store_true", help="leave example values out of the reports (use for personal data)")
    _common(p)
    p.set_defaults(func=cmd_profile)

    p = sub.add_parser("map-coa", help="map a source chart of accounts to a target chart", description="Apply a manual mapping first, then suggest mappings by account type and name similarity.")
    p.add_argument("--source", required=True, help="source chart of accounts CSV")
    p.add_argument("--target", required=True, help="target chart of accounts CSV")
    p.add_argument("--manual", help="manual mapping CSV with source_account and target_account")
    p.add_argument("--tb", help="source trial balance CSV, used to flag accounts that carry a balance")
    p.add_argument("--source-map", help="column names in the source chart, e.g. account=acct_no,name=acct_name,type=acct_type")
    p.add_argument("--target-map", help="column names in the target chart")
    p.add_argument("--tb-map", help="column names in the trial balance, e.g. period=per,account=acct")
    p.add_argument("--decimal-comma", action="store_true", help="trial balance amounts use 1.234,56 style")
    p.add_argument("--min-confidence", type=float, default=0.65, help="lowest similarity that produces a suggestion (default 0.65)")
    p.add_argument("--high-confidence", type=float, default=0.85, help="similarity treated as high confidence (default 0.85)")
    p.add_argument("--fail-on-unapproved", action="store_true", help="exit with status 3 if any account lacks an approved mapping")
    _common(p)
    p.set_defaults(func=cmd_map_coa)

    p = sub.add_parser("dedupe", help="find probable duplicate customers, suppliers or parts", description="Score pairs within and across two systems. Writes a match report and a merge proposal. Changes no data.")
    p.add_argument("--entity", choices=["party", "part"], required=True, help="party for customers or suppliers, part for parts")
    p.add_argument("--a", required=True, help="CSV from system A")
    p.add_argument("--b", help="CSV from system B (optional)")
    p.add_argument("--a-map", help="column names in the A file, e.g. id=cust_id,name=cust_name,tax=vat_no")
    p.add_argument("--b-map", help="column names in the B file (defaults to the A mapping)")
    p.add_argument("--a-label", default="ERP A")
    p.add_argument("--b-label", default="ERP B")
    p.add_argument("--auto", type=int, default=dedupe.AUTO_THRESHOLD, help=f"score for an automatic match (default {dedupe.AUTO_THRESHOLD})")
    p.add_argument("--review", type=int, default=dedupe.REVIEW_THRESHOLD, help=f"score for review (default {dedupe.REVIEW_THRESHOLD})")
    p.add_argument("--legal-suffixes", help="extra legal form words to strip from names, comma separated")
    p.add_argument("--uom-map", help="extra unit aliases for parts, e.g. KAR=CTN,STCK=EA")
    _common(p)
    p.set_defaults(func=cmd_dedupe)

    p = sub.add_parser("reconcile", help="compare trial balances before and after a chart mapping", description="Check that a chart mapping keeps balances intact, period by period, within a tolerance.")
    p.add_argument("--tb", required=True, help="source trial balance CSV")
    p.add_argument("--mapping", required=True, help="mapping CSV: map-coa output or a manual file")
    p.add_argument("--source-coa", required=True)
    p.add_argument("--target-coa", required=True)
    p.add_argument("--target-tb", help="trial balance loaded into the target in a trial migration, to compare with the mapped source")
    p.add_argument("--tolerance", default="0.01", help="largest absolute difference treated as zero (default 0.01)")
    p.add_argument("--include-suggested", action="store_true", help="also use suggested mappings from a map-coa file (preview only)")
    p.add_argument("--source-map", help="column names in the source chart")
    p.add_argument("--target-map", help="column names in the target chart")
    p.add_argument("--tb-map", help="column names in the trial balance: period, account, debit, credit, balance")
    p.add_argument("--target-tb-map", help="column names in the target trial balance (defaults to --tb-map)")
    p.add_argument("--decimal-comma", action="store_true", help="amounts use 1.234,56 style")
    p.add_argument("--allow-reclassification", action="store_true", help="list reclassifications between account classes but do not count them as differences, once they are signed off")
    p.add_argument("--fail-on-difference", action="store_true", help="exit with status 3 if any period has differences")
    _common(p)
    p.set_defaults(func=cmd_reconcile)

    p = sub.add_parser("readiness", help="go or no go scorecard from the other commands' summaries", description="Combine profile, mapping and duplicate summaries (and optionally reconcile) into a scorecard.")
    p.add_argument("inputs", nargs="+", help="*-summary.json files written by the other commands")
    p.add_argument("--thresholds", help="JSON file overriding default thresholds")
    p.add_argument("--fail-on-no-go", action="store_true", help="exit with status 3 when the verdict is NO-GO")
    p.add_argument("--out", default="output")
    p.add_argument("--name")
    p.set_defaults(func=cmd_readiness)

    p = sub.add_parser("decide", help="scored consolidate, partially integrate or keep separate decision", description="Score a consolidation decision from a CSV of criterion scores and gate answers.")
    p.add_argument("--scores", required=True, help="CSV with id, value and evidence")
    p.add_argument("--criteria", help="criteria CSV (default: decision/criteria.csv)")
    _common(p)
    p.set_defaults(func=cmd_decide)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE
    except BrokenPipeError:  # pragma: no cover
        return EXIT_OK
