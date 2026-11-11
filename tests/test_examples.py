"""End to end runs on the synthetic examples, checked against planted truth."""

import csv
import filecmp
import json
import os
import subprocess
import sys

import pytest

from erp_consol import coa
from erp_consol.csvio import read_table

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "examples")
sys.path.insert(0, EX)


def tree(path):
    return sorted(os.path.relpath(os.path.join(d, f), path) for d, _, fs in os.walk(path) for f in fs)


def assert_same_tree(committed, fresh):
    assert tree(committed) == tree(fresh)
    for rel in tree(committed):
        assert filecmp.cmp(os.path.join(committed, rel), os.path.join(fresh, rel), shallow=False), f"{rel} differs"


@pytest.fixture(scope="module")
def fresh_reports(tmp_path_factory):
    import run_examples

    out = tmp_path_factory.mktemp("reports")
    assert run_examples.run(str(out)) == 0
    return str(out)


def test_generated_data_matches_committed_files(tmp_path):
    import generate_examples

    generate_examples.main(str(tmp_path))
    assert_same_tree(os.path.join(EX, "data"), str(tmp_path / "data"))
    assert_same_tree(os.path.join(EX, "truth"), str(tmp_path / "truth"))


def test_generation_script_runs_from_the_command_line(tmp_path):
    result = subprocess.run([sys.executable, os.path.join(EX, "generate_examples.py"), str(tmp_path)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert "ERP A chart: 81 accounts; ERP B chart: 110 accounts" in result.stdout


def test_committed_reports_match_a_fresh_run(fresh_reports):
    assert_same_tree(os.path.join(EX, "reports"), fresh_reports)


def test_python_dash_m_entry_point(tmp_path):
    result = subprocess.run([sys.executable, "-m", "erp_consol", "decide", "--scores", os.path.join(ROOT, "decision/examples/two-uk-distributors.csv"),
                             "--out", str(tmp_path)], capture_output=True, text=True, cwd=ROOT)
    assert result.returncode == 0 and "CONSOLIDATE" in result.stdout
    bad = subprocess.run([sys.executable, "-m", "erp_consol", "profile", "no-such-file.csv"], capture_output=True, text=True, cwd=ROOT)
    assert bad.returncode == 2 and bad.stderr.startswith("error: ") and "Traceback" not in bad.stderr


def load_json(fresh, rel):
    with open(os.path.join(fresh, rel), encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Duplicate detection against planted pairs


def planted(kind):
    with open(os.path.join(EX, "truth", f"expected_pairs_{kind}.csv"), encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.parametrize("kind", ["customers", "suppliers", "parts"])
def test_every_planted_pair_lands_in_an_acceptable_band(fresh_reports, kind):
    found = {}
    with open(os.path.join(fresh_reports, "dedupe", f"{kind}.matches.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            found[(r["left_system"], r["left_id"], r["right_system"], r["right_id"])] = r["band"]
    rows = planted(kind)
    assert len(rows) >= 14
    for r in rows:
        key = (r["left_system"], r["left_id"], r["right_system"], r["right_id"])
        band = found.get(key, "none")
        assert band in r["acceptable_bands"].split("|"), f"{key} expected {r['acceptable_bands']} ({r['scenario']}) but got {band}"


@pytest.mark.parametrize("kind", ["customers", "suppliers", "parts"])
def test_pairs_that_must_not_merge_automatically_are_never_automatic(fresh_reports, kind):
    found = {}
    with open(os.path.join(fresh_reports, "dedupe", f"{kind}.matches.csv"), encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            found[(r["left_system"], r["left_id"], r["right_system"], r["right_id"])] = r["band"]
    for r in planted(kind):
        if "auto" not in r["acceptable_bands"].split("|"):
            key = (r["left_system"], r["left_id"], r["right_system"], r["right_id"])
            assert found.get(key, "none") != "auto"


def test_known_miss_is_documented_and_really_missed(fresh_reports):
    # Parts renumbered in ERP B with no drawing number cannot be found: the model has no evidence to use.
    missed = [r for r in planted("parts") if r["scenario"] == "cross system, s4"]
    assert len(missed) == 3
    with open(os.path.join(fresh_reports, "dedupe", "parts.matches.csv"), encoding="utf-8") as fh:
        pairs = {(r["left_id"], r["right_id"]) for r in csv.DictReader(fh)}
    assert not any((m["left_id"], m["right_id"]) in pairs for m in missed)


def test_headline_dedupe_numbers(fresh_reports):
    c = load_json(fresh_reports, "dedupe/customers.dedupe-summary.json")
    assert (c["records"], c["auto_pairs"], c["review_pairs"], c["clusters_spanning_both_systems"]) == (94, 16, 10, 9)
    s = load_json(fresh_reports, "dedupe/suppliers.dedupe-summary.json")
    assert (s["records"], s["auto_pairs"], s["review_pairs"], s["clusters_spanning_both_systems"]) == (64, 10, 7, 5)
    p = load_json(fresh_reports, "dedupe/parts.dedupe-summary.json")
    assert (p["records"], p["auto_pairs"], p["review_pairs"], p["clusters_spanning_both_systems"]) == (106, 22, 10, 17)


def test_merge_proposal_never_changes_source_data(fresh_reports):
    with open(os.path.join(fresh_reports, "dedupe", "customers.merge-proposal.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert rows and all("after review" in r["action"] or r["role"] == "survivor" for r in rows)
    sizes = {}
    for r in rows:
        sizes.setdefault(r["cluster_id"], []).append(r)
    assert all(len(v) == int(v[0]["cluster_size"]) and sum(1 for x in v if x["role"] == "survivor") == 1 for v in sizes.values())


# ---------------------------------------------------------------------------
# Chart of accounts


def truth_map(system):
    with open(os.path.join(EX, "truth", f"coa_truth_erp_{system}.csv"), encoding="utf-8") as fh:
        return {r["source_account"]: r["target_account"] for r in csv.DictReader(fh)}


def suggest_only(system):
    cols = {"a": {"account": "acct_no", "name": "acct_name", "type": "acct_type"},
            "b": {"account": "gl_code", "name": "gl_description", "type": "class"}}[system]
    enc = "cp1252" if system == "b" else "utf-8"
    src = coa.load_chart(read_table(os.path.join(EX, "data", f"erp_{system}_chart.csv"), encoding=enc), cols)
    tgt = coa.load_chart(read_table(os.path.join(EX, "data", "target_chart.csv")), {})
    rows, _, _ = coa.map_chart(src, tgt, [])
    return rows, truth_map(system)


def test_chart_sizes():
    for name, n in (("erp_a_chart", 81), ("erp_b_chart", 110)):
        t = read_table(os.path.join(EX, "data", f"{name}.csv"))
        assert len(t.rows) == n
    codes_a = {r["acct_no"] for r in read_table(os.path.join(EX, "data", "erp_a_chart.csv")).rows}
    codes_b = {r["gl_code"] for r in read_table(os.path.join(EX, "data", "erp_b_chart.csv")).rows}
    assert max(len(c) for c in codes_a) == 4 and min(len(c) for c in codes_b) == 6  # different numbering schemes


def test_suggester_accuracy_is_what_the_docs_say():
    """Numbers quoted in docs/scoring-models.md. If the algorithm changes, update the docs with these."""
    result = {}
    for system in ("a", "b"):
        rows, truth = suggest_only(system)
        high = [r for r in rows if r["status"] == "review" and "low_confidence" not in r["flags"]]
        low = [r for r in rows if r["status"] == "review" and "low_confidence" in r["flags"]]
        right = lambda rs: sum(1 for r in rs if truth[r["source_account"]] == r["target_account"])
        result[system] = (len(rows), len(high), right(high), len(low), right(low),
                          sum(1 for r in rows if r["status"] == "unmapped"))
    assert result["a"] == (81, 40, 40, 21, 18, 20)
    assert result["b"] == (110, 35, 33, 34, 23, 41)


def test_suggestions_are_never_approved(fresh_reports):
    with open(os.path.join(fresh_reports, "coa", "erp_b.mapping.csv"), encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    assert all(r["status"] != "approved" for r in rows if r["method"] == "suggested")
    assert sum(1 for r in rows if r["status"] == "approved") == 55


def test_planted_manual_mapping_errors_are_caught(fresh_reports):
    with open(os.path.join(fresh_reports, "coa", "erp_b.exceptions.csv"), encoding="utf-8") as fh:
        issues = {r["issue"] for r in csv.DictReader(fh)}
    assert {"manual_target_unknown", "manual_source_unknown", "many_to_one", "unmapped", "type_unknown"} <= issues
    with open(os.path.join(fresh_reports, "coa", "erp_a.exceptions.csv"), encoding="utf-8") as fh:
        a_issues = {r["issue"] for r in csv.DictReader(fh)}
    assert "type_mismatch" in a_issues  # the proposed policy change to capitalise carriage


# ---------------------------------------------------------------------------
# Reconciliation and readiness


def test_reconcile_erp_a_finds_the_planted_load_problems(fresh_reports):
    s = load_json(fresh_reports, "reconcile/erp_a.reconcile-summary.json")
    assert s["unmapped_accounts_with_balance"] == 0
    assert s["target_tb_differences"] == 2  # a 1,250.00 difference and a missing account; the 0.03 and 0.02 are inside tolerance
    with open(os.path.join(fresh_reports, "reconcile", "erp_a.reconcile-differences.csv"), encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if r["type"] == "target_tb_difference"]
    assert sorted((r["period"], r["difference"]) for r in rows)[0] == ("2026-02", "1250.00")
    assert len(rows) == 2


def test_reconcile_erp_b_shows_what_unapproved_mapping_costs(fresh_reports):
    s = load_json(fresh_reports, "reconcile/erp_b.reconcile-summary.json")
    assert s["unmapped_accounts_with_balance"] == 55 and s["periods_with_differences"] == 3
    preview = load_json(fresh_reports, "reconcile/erp_b_preview.reconcile-summary.json")
    assert preview["unmapped_accounts_with_balance"] < s["unmapped_accounts_with_balance"]


def test_source_trial_balances_balance_in_every_period(fresh_reports):
    for name in ("erp_a", "erp_b"):
        s = load_json(fresh_reports, f"reconcile/{name}.reconcile-summary.json")
        assert all(p["source_net"] == "0.00" for p in s["periods_detail"])


def test_group_readiness_verdict(fresh_reports):
    r = load_json(fresh_reports, "readiness/group-readiness-summary.json")
    assert r["verdict"] == "NO-GO" and r["missing_evidence"] == []
    failing = {(c["subject"], c["metric"]) for c in r["checks"] if c["status"] == "RED"}
    assert ("erp_b", "coa.approved_coverage") in failing
    green = {(c["subject"], c["metric"]) for c in r["checks"] if c["status"] == "GREEN"}
    assert ("erp_a", "coa.balance_accounts_not_approved") in green


def test_committed_example_data_is_fictional_and_decodes():
    for name in os.listdir(os.path.join(EX, "data")):
        t = read_table(os.path.join(EX, "data", name))
        assert t.rows, name
