#!/usr/bin/env python3
"""Regenerate every committed example report.

    python examples/run_examples.py            # writes to examples/reports
    python examples/run_examples.py OUTDIR     # writes elsewhere, used by the tests

Each step is an ordinary erp_consol command line, so the README commands and the
committed reports cannot drift apart: the test suite runs this script and compares
the result with the committed files.
"""

from __future__ import annotations

import contextlib
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

from erp_consol.cli import main  # noqa: E402

D = "examples/data"
C = "examples/config"

A_CUST = "id=cust_id,name=cust_name,postcode=postcode,tax=vat_no,country=country,email=email,city=city"
B_CUST = "id=account_no,name=account_name,postcode=zip,tax=tax_id,country=country_code,email=contact_email,city=town"
A_SUPP = A_CUST.replace("id=cust_id,name=cust_name", "id=supplier_id,name=supplier_name")
A_PART = "part_number=part_no,description=description,uom=uom,drawing=drawing_no,category=category"
B_PART = "part_number=item_no,description=item_text,uom=unit,drawing=drawing,category=item_group"
A_COA = "account=acct_no,name=acct_name,type=acct_type"
B_COA = "account=gl_code,name=gl_description,type=class"


def steps(out: str) -> list[list[str]]:
    p = lambda sub: os.path.join(out, sub)
    s: list[list[str]] = []
    for name in ("erp_a_customers", "erp_b_customers", "erp_a_suppliers", "erp_b_suppliers", "erp_a_parts", "erp_b_parts"):
        s.append(["profile", f"{D}/{name}.csv", "--config", f"{C}/{name}.json", "--out", p("profile")])
    s.append(["map-coa", "--source", f"{D}/erp_a_chart.csv", "--target", f"{D}/target_chart.csv", "--manual", f"{D}/erp_a_manual_mapping.csv",
              "--tb", f"{D}/erp_a_trial_balance.csv", "--source-map", A_COA, "--target-map", "account=account", "--tb-map", "account=acct_no",
              "--name", "erp_a", "--out", p("coa")])
    s.append(["map-coa", "--source", f"{D}/erp_b_chart.csv", "--target", f"{D}/target_chart.csv", "--manual", f"{D}/erp_b_manual_mapping.csv",
              "--tb", f"{D}/erp_b_trial_balance.csv", "--source-map", B_COA, "--target-map", "account=account", "--tb-map", "account=gl_code",
              "--decimal-comma", "--name", "erp_b", "--out", p("coa")])
    s.append(["dedupe", "--entity", "party", "--a", f"{D}/erp_a_customers.csv", "--b", f"{D}/erp_b_customers.csv",
              "--a-map", A_CUST, "--b-map", B_CUST, "--name", "customers", "--out", p("dedupe")])
    s.append(["dedupe", "--entity", "party", "--a", f"{D}/erp_a_suppliers.csv", "--b", f"{D}/erp_b_suppliers.csv",
              "--a-map", A_SUPP, "--b-map", B_CUST, "--name", "suppliers", "--out", p("dedupe")])
    s.append(["dedupe", "--entity", "part", "--a", f"{D}/erp_a_parts.csv", "--b", f"{D}/erp_b_parts.csv",
              "--a-map", A_PART, "--b-map", B_PART, "--uom-map", "CTN=BOX", "--name", "parts", "--out", p("dedupe")])
    s.append(["reconcile", "--tb", f"{D}/erp_a_trial_balance.csv", "--mapping", p("coa/erp_a.mapping.csv"), "--source-coa", f"{D}/erp_a_chart.csv",
              "--target-coa", f"{D}/target_chart.csv", "--source-map", A_COA, "--tb-map", "account=acct_no",
              "--target-tb", f"{D}/erp_a_loaded_target_tb.csv", "--target-tb-map", "account=account", "--tolerance", "0.05",
              "--name", "erp_a", "--out", p("reconcile")])
    s.append(["reconcile", "--tb", f"{D}/erp_b_trial_balance.csv", "--mapping", p("coa/erp_b.mapping.csv"), "--source-coa", f"{D}/erp_b_chart.csv",
              "--target-coa", f"{D}/target_chart.csv", "--source-map", B_COA, "--tb-map", "account=gl_code", "--decimal-comma",
              "--name", "erp_b", "--out", p("reconcile")])
    s.append(["reconcile", "--tb", f"{D}/erp_b_trial_balance.csv", "--mapping", p("coa/erp_b.mapping.csv"), "--include-suggested",
              "--source-coa", f"{D}/erp_b_chart.csv", "--target-coa", f"{D}/target_chart.csv", "--source-map", B_COA,
              "--tb-map", "account=gl_code", "--decimal-comma", "--name", "erp_b_preview", "--out", p("reconcile")])
    summaries = [p(f"profile/{n}.profile-summary.json") for n in
                 ("erp_a_customers", "erp_b_customers", "erp_a_suppliers", "erp_b_suppliers", "erp_a_parts", "erp_b_parts")]
    summaries += [p("coa/erp_a.coa-summary.json"), p("coa/erp_b.coa-summary.json")]
    summaries += [p(f"dedupe/{n}.dedupe-summary.json") for n in ("customers", "suppliers", "parts")]
    summaries += [p("reconcile/erp_a.reconcile-summary.json"), p("reconcile/erp_b.reconcile-summary.json")]
    s.append(["readiness", *summaries, "--name", "group-readiness", "--out", p("readiness")])
    for name in ("two-manufacturers", "two-uk-distributors", "different-regulated-businesses"):
        s.append(["decide", "--scores", f"decision/examples/{name}.csv", "--out", p("decision")])
    return s


def run(out: str, quiet: bool = True) -> int:
    os.chdir(ROOT)
    for argv in steps(out):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = main(argv)
        if not quiet:
            sys.stdout.write(buf.getvalue())
        if code != 0:
            sys.stderr.write(f"step failed with status {code}: {' '.join(argv)}\n")
            return code
    return 0


if __name__ == "__main__":
    # The commands use paths relative to the repository root, so the default output folder is too.
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else "examples/reports", quiet=False))
