#!/usr/bin/env python3
"""Generate the synthetic example extracts for two fictional manufacturers.

Run from the repository root or from this folder:

    python examples/generate_examples.py            # writes examples/data and examples/truth
    python examples/generate_examples.py OUTDIR     # writes OUTDIR/data and OUTDIR/truth

The script uses only the standard library, a fixed seed and sorted output, so every run
produces identical files.
It does not import erp_consol: the data must not depend on the code it tests.

The group, companies, people, addresses, tax numbers and balances are invented.
Tax numbers are random digits and are not checked against any register.
"""

from __future__ import annotations

import csv
import os
import random
import sys
from decimal import ROUND_HALF_UP, Decimal

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from _concepts import (  # noqa: E402
    A_BASE, A_EXTRAS, A_TYPE_LABEL, B_BASE, B_EXTRAS, B_TYPE_LABEL, CONCEPTS, GROUP_TARGET,
)
import _masters  # noqa: E402

SEED = 2026
PERIODS = ["2026-01", "2026-02", "2026-03"]
DATA = os.path.join(HERE, "data")
TRUTH = os.path.join(HERE, "truth")
CENT = Decimal("0.01")

A_TYPE_OVERRIDE = {"Bank Current Account": "Bank", "Corporation Tax Payable": "Taxation", "Corporation Tax Charge": "Taxation"}


def write_csv(path, header, rows, *, delimiter=",", encoding="utf-8"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding=encoding, newline="") as fh:
        w = csv.writer(fh, delimiter=delimiter, lineterminator="\n")
        w.writerow(header)
        w.writerows(rows)


def q(x):
    return Decimal(x).quantize(CENT, rounding=ROUND_HALF_UP)


# ---------------------------------------------------------------------------
# Charts
# ---------------------------------------------------------------------------


def build_charts():
    target, a_chart, b_chart = [], [], []
    target_code_by_name = {}
    for group, (header, gname, gtype) in GROUP_TARGET.items():
        target.append([header, gname, gtype, gname, "n"])
        i = 0
        for g, tname, _a, _b in CONCEPTS:
            if g != group:
                continue
            i += 1
            code = header + 10 * i
            target.append([code, tname, gtype, gname, "y"])
            target_code_by_name[tname] = code
    # source accounts: (code, name, label, group, concept target name or None, concept index)
    a_accounts, b_accounts = [], []
    for group in GROUP_TARGET:
        ai, bi = 0, 0
        for g, tname, aname, bnames in CONCEPTS:
            if g != group:
                continue
            if aname:
                ai += 1
                a_accounts.append((str(A_BASE[group] + 10 * ai), aname, A_TYPE_OVERRIDE.get(aname, A_TYPE_LABEL[group]), group, tname))
            if bnames:
                bi += 1
                for k, bn in enumerate(bnames):
                    b_accounts.append((str(B_BASE[group] + 100 * bi + 10 * k), bn, B_TYPE_LABEL[group], group, tname))
        for g, name, truth in A_EXTRAS:
            if g == group:
                ai += 1
                a_accounts.append((str(A_BASE[group] + 10 * ai), name, A_TYPE_OVERRIDE.get(name, A_TYPE_LABEL[group]), group, truth))
        for g, name, truth in B_EXTRAS:
            if g == group:
                bi += 1
                b_accounts.append((str(B_BASE[group] + 100 * bi), name, B_TYPE_LABEL[group], group, truth))
    return target, target_code_by_name, a_accounts, b_accounts


# ---------------------------------------------------------------------------
# Trial balances
# ---------------------------------------------------------------------------


def magnitude(group, name, rng):
    n = name.lower()
    if group == "FA":
        if "accumulated" in n:
            return rng.uniform(100_000, 1_200_000), "bs"
        if "software" in n:
            return rng.uniform(20_000, 200_000), "bs"
        return rng.uniform(250_000, 2_500_000), "bs"
    if group == "CA":
        if "inventory" in n:
            return rng.uniform(150_000, 900_000), "bs"
        if "trade receivables" in n:
            return rng.uniform(600_000, 2_000_000), "bs"
        if "bank" in n:
            return rng.uniform(40_000, 400_000), "bs"
        if "petty" in n:
            return rng.uniform(500, 3_000), "bs"
        return rng.uniform(5_000, 150_000), "bs"
    if group == "CL":
        if "trade payables" in n:
            return rng.uniform(400_000, 1_200_000), "bs"
        if "vat" in n:
            return rng.uniform(20_000, 120_000), "bs"
        return rng.uniform(10_000, 300_000), "bs"
    if group == "LL":
        return rng.uniform(150_000, 1_500_000), "bs"
    if group == "EQ":
        if "share capital" in n:
            return rng.uniform(100_000, 500_000), "bs"
        return rng.uniform(50_000, 300_000), "bs"
    if group == "REV":
        if n.startswith("revenue, castings"):
            return rng.uniform(300_000, 1_200_000), "pl"
        return rng.uniform(2_000, 60_000), "pl"
    if group == "COS":
        if "raw materials" in n:
            return rng.uniform(150_000, 700_000), "pl"
        if "labour" in n:
            return rng.uniform(80_000, 300_000), "pl"
        return rng.uniform(3_000, 90_000), "pl"
    if group == "OH":
        return rng.uniform(2_000, 120_000), "pl"
    return rng.uniform(500, 30_000), "pl"


def natural_sign(group, name):
    n = name.lower()
    if group == "FA":
        return -1 if "accumulated" in n else 1
    if group == "CA":
        return -1 if ("allowance" in n or "provision" in n) else 1
    if group in ("CL", "LL", "EQ", "FINI"):
        return -1
    if group == "REV":
        return 1 if "returns" in n else -1
    return 1


def build_tb(system, accounts, plug_name, scale):
    """Return {period: {account code: Decimal net}} for the system's accounts."""
    by_concept = {}
    for code, name, _label, group, tname in accounts:
        by_concept.setdefault((group, tname if tname else f"extra:{name}"), []).append((code, name))
    tb = {p: {} for p in PERIODS}
    for (group, concept), members in sorted(by_concept.items()):
        extra = concept.startswith("extra:")
        label = members[0][1] if extra else concept
        if system == "A" and extra:
            continue  # ERP A extras carry no balance in the example
        rng = random.Random(f"{SEED}:{system}:{concept}")
        mag, kind = magnitude(group, label, rng)
        mag *= scale
        sign = natural_sign(group, label)
        if kind == "bs":
            totals = {p: mag * (1 + rng.uniform(-0.03, 0.03) * (k + 1)) for k, p in enumerate(PERIODS)}
        else:
            running, totals = 0.0, {}
            for p in PERIODS:
                running += mag * (1 + rng.uniform(-0.08, 0.08))
                totals[p] = running
        shares = [rng.uniform(0.2, 1.0) for _ in members]
        s = sum(shares)
        for p in PERIODS:
            total = q(sign * totals[p])
            parts = [q(total * Decimal(str(round(sh / s, 6)))) for sh in shares]
            parts[-1] = total - sum(parts[:-1], Decimal(0))
            for (code, _n), v in zip(members, parts):
                tb[p][code] = v
    plug_code = next(c for c, n, *_ in accounts if n == plug_name)
    for p in PERIODS:
        residual = -sum((v for c, v in tb[p].items() if c != plug_code), Decimal(0))
        tb[p][plug_code] = residual
    return tb


def write_tb(path, tb, *, delimiter=",", decimal_comma=False, encoding="utf-8", header):
    rows = []
    for p in PERIODS:
        for code in sorted(tb[p], key=lambda c: (len(c), c)):
            v = tb[p][code]
            if v == 0:
                continue
            fmt = lambda x: (f"{x:.2f}".replace(".", ",") if decimal_comma else f"{x:.2f}")
            rows.append([p, code, fmt(v) if v > 0 else "", fmt(-v) if v < 0 else ""])
    write_csv(path, header, rows, delimiter=delimiter, encoding=encoding)


# ---------------------------------------------------------------------------


def main(out_root=None):
    data_dir = os.path.join(out_root, "data") if out_root else DATA
    truth_dir = os.path.join(out_root, "truth") if out_root else TRUTH
    rng = random.Random(SEED)
    target, tcode, a_accounts, b_accounts = build_charts()

    write_csv(os.path.join(data_dir, "target_chart.csv"), ["account", "name", "type", "group", "postable"], target)
    write_csv(os.path.join(data_dir, "erp_a_chart.csv"), ["acct_no", "acct_name", "acct_type"],
              [[c, n, l] for c, n, l, *_ in a_accounts])
    write_csv(os.path.join(data_dir, "erp_b_chart.csv"), ["gl_code", "gl_description", "class"],
              [[c, n, l] for c, n, l, *_ in b_accounts], delimiter=";", encoding="cp1252")

    # Truth: what a careful accountant would map each source account to (empty: the target needs a new account).
    def truth_rows(accounts):
        out = []
        for code, name, _l, _g, tname in accounts:
            out.append([code, name, tcode.get(tname, "") if tname else ""])
        return out

    write_csv(os.path.join(truth_dir, "coa_truth_erp_a.csv"), ["source_account", "source_name", "target_account"], truth_rows(a_accounts))
    write_csv(os.path.join(truth_dir, "coa_truth_erp_b.csv"), ["source_account", "source_name", "target_account"], truth_rows(b_accounts))

    # Manual mapping files: the work agreed so far. ERP A is complete apart from the accounts that need a new
    # target account. ERP B is about half done and contains two deliberate mistakes for the tool to catch.
    a_manual = []
    for code, name, _l, _g, tname in a_accounts:
        if tname and tname in tcode:
            note = "agreed with group finance"
            target_code = tcode[tname]
            if name == "Carriage Inwards":
                target_code = tcode["Raw materials inventory"]
                note = "proposed policy change: capitalise carriage into stock, needs sign-off"
            a_manual.append([code, target_code, note])
    write_csv(os.path.join(data_dir, "erp_a_manual_mapping.csv"), ["source_account", "target_account", "note"], a_manual)

    mappable_b = [(c, n, t) for c, n, _l, _g, t in b_accounts if t and t in tcode]
    chosen = [m for m in mappable_b if rng.random() < 0.55]
    b_manual = []
    for code, name, tname in chosen:
        target_code = tcode[tname]
        if name == "Bank USD account":
            target_code = 12999  # deliberate error: not a target account
        b_manual.append([code, target_code, "agreed with group finance"])
    if not any(r[1] == 12999 for r in b_manual):
        usd = next(c for c, n, *_ in b_accounts if n == "Bank USD account")
        b_manual.append([usd, 12999, "typed from memory"])
    b_manual.append(["999999", tcode["Suspense and clearing"], "account closed last year"])
    b_manual.sort(key=lambda r: (len(str(r[0])), str(r[0])))
    write_csv(os.path.join(data_dir, "erp_b_manual_mapping.csv"), ["source_account", "target_account", "note"], b_manual)

    # Trial balances
    tb_a = build_tb("A", a_accounts, "Profit & Loss Reserve", 1.0)
    tb_b = build_tb("B", b_accounts, "Retained earnings brought forward", 0.85)
    write_tb(os.path.join(data_dir, "erp_a_trial_balance.csv"), tb_a, header=["period", "acct_no", "debit", "credit"])
    write_tb(os.path.join(data_dir, "erp_b_trial_balance.csv"), tb_b, delimiter=";", decimal_comma=True, encoding="cp1252",
             header=["period", "gl_code", "debit", "credit"])

    # Trial balance as loaded into the target in a trial migration of ERP A, with deliberate load problems.
    a_map = {r[0]: str(r[1]) for r in a_manual}
    loaded = {p: {} for p in PERIODS}
    for p in PERIODS:
        for code, v in tb_a[p].items():
            if code in a_map:
                loaded[p][a_map[code]] = loaded[p].get(a_map[code], Decimal(0)) + v
    loaded["2026-01"][str(tcode["Trade payables"])] += Decimal("0.03")      # rounding, inside tolerance
    loaded["2026-02"][str(tcode["Accruals"])] -= Decimal("0.02")            # rounding, inside tolerance
    loaded["2026-02"][str(tcode["Trade receivables"])] += Decimal("1250.00")  # a real difference
    loaded["2026-03"].pop(str(tcode["Telephone and internet"]), None)       # a missing account
    write_tb(os.path.join(data_dir, "erp_a_loaded_target_tb.csv"), loaded, header=["period", "account", "debit", "credit"])

    _masters.generate(data_dir, truth_dir, SEED)
    print(f"ERP A chart: {len(a_accounts)} accounts; ERP B chart: {len(b_accounts)} accounts; target chart: {len(target)} rows")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
