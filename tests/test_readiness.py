import json

import pytest

from erp_consol import readiness
from erp_consol.errors import InputError

TH = readiness.load_thresholds(None)


def profile(**kw):
    base = {"kind": "profile", "name": "customers", "required_max_missing_rate": 0.0, "key_duplicate_rate": 0.0, "format_invalid_rate": 0.0}
    base.update(kw)
    return base


def coa(**kw):
    base = {"kind": "coa", "name": "erp_a", "approved_coverage": 1.0, "balance_accounts_not_approved": 0, "exceptions_error": 0}
    base.update(kw)
    return base


def dedupe(**kw):
    base = {"kind": "dedupe", "name": "customers", "review_pairs_per_100_records": 1.0,
            "systems": {"A": {"label": "ERP A", "within_duplicate_rate": 0.0}, "B": {"label": "ERP B", "within_duplicate_rate": 0.0}}}
    base.update(kw)
    return base


def evaluate(*summaries):
    return readiness.evaluate(list(summaries), TH)


def test_all_green_is_go():
    r = evaluate(profile(), coa(), dedupe())
    assert r["verdict"] == "GO" and r["red"] == 0 and r["amber"] == 0
    assert r["green"] == 3 + 3 + 3


def test_one_amber_is_conditional_go():
    r = evaluate(profile(format_invalid_rate=0.03), coa(), dedupe())
    assert r["verdict"] == "CONDITIONAL GO" and r["amber"] == 1 and r["red"] == 0


def test_one_red_is_no_go():
    r = evaluate(profile(), coa(approved_coverage=0.5), dedupe())
    assert r["verdict"] == "NO-GO" and r["red"] == 1


@pytest.mark.parametrize("value, status", [(0.02, "GREEN"), (0.0201, "AMBER"), (0.05, "AMBER"), (0.0501, "RED")])
def test_threshold_edges_lower_is_better(value, status):
    r = evaluate(profile(required_max_missing_rate=value), coa(), dedupe())
    chk = next(c for c in r["checks"] if c["metric"] == "profile.required_missing_rate")
    assert chk["status"] == status


@pytest.mark.parametrize("value, status", [(0.98, "GREEN"), (0.979, "AMBER"), (0.90, "AMBER"), (0.899, "RED")])
def test_threshold_edges_higher_is_better(value, status):
    r = evaluate(profile(), coa(approved_coverage=value), dedupe())
    chk = next(c for c in r["checks"] if c["metric"] == "coa.approved_coverage")
    assert chk["status"] == status


def test_zero_tolerance_checks():
    r = evaluate(profile(), coa(balance_accounts_not_approved=1), dedupe())
    chk = next(c for c in r["checks"] if c["metric"] == "coa.balance_accounts_not_approved")
    assert chk["status"] == "RED"


def test_missing_evidence_prevents_go():
    r = evaluate(profile(), coa())
    assert r["verdict"] == "NO-GO" and r["missing_evidence"] == ["duplicate analysis"]
    assert evaluate()["missing_evidence"] == ["chart of accounts mapping", "data quality profile", "duplicate analysis"]


def test_not_assessed_measures_are_listed_not_scored():
    r = evaluate(profile(key_duplicate_rate=None, format_invalid_rate=None, required_max_missing_rate=None), coa(), dedupe())
    assert len(r["not_assessed"]) == 3
    assert r["verdict"] == "GO"  # unassessed measures neither pass nor fail: the report lists them


def test_each_system_is_checked_separately():
    d = dedupe(systems={"A": {"label": "ERP A", "within_duplicate_rate": 0.0}, "B": {"label": "ERP B", "within_duplicate_rate": 0.04}})
    r = evaluate(profile(), coa(), d)
    bad = [c for c in r["checks"] if c["status"] == "RED"]
    assert len(bad) == 1 and "ERP B" in bad[0]["subject"]


def test_reconcile_difference_is_red():
    r = evaluate(profile(), coa(), dedupe(), {"kind": "reconcile", "name": "erp_a", "periods_with_differences": 1})
    assert r["verdict"] == "NO-GO"


def test_unrecognised_summary_rejected():
    with pytest.raises(InputError, match="Unrecognised summary"):
        evaluate({"kind": "something"})


def test_threshold_overrides():
    th = readiness.load_thresholds({"profile.format_invalid_rate": {"green": 0.05, "amber": 0.10}})
    r = readiness.evaluate([profile(format_invalid_rate=0.04), coa(), dedupe()], th)
    assert r["verdict"] == "GO"


@pytest.mark.parametrize("override, message", [
    ({"nope": {"green": 1, "amber": 2}}, "Unknown threshold"),
    ({"profile.format_invalid_rate": {"green": 1}}, "must look like"),
    ({"profile.format_invalid_rate": {"green": "a", "amber": 2}}, "must be a number"),
    ({"profile.format_invalid_rate": {"green": 0.2, "amber": 0.1}}, "no greater than"),
    ({"coa.approved_coverage": {"green": 0.5, "amber": 0.9}}, "no less than"),
])
def test_bad_threshold_overrides(override, message):
    with pytest.raises(InputError, match=message):
        readiness.load_thresholds(override)


def test_defaults_are_internally_consistent():
    for key, spec in readiness.DEFAULT_THRESHOLDS.items():
        if spec["direction"] == "lower":
            assert spec["green"] <= spec["amber"], key
        else:
            assert spec["green"] >= spec["amber"], key


def test_markdown_lists_reds_first_and_states_the_rule():
    md = readiness.render_markdown(evaluate(profile(), coa(approved_coverage=0.5, balance_accounts_not_approved=2), dedupe()), TH)
    assert "**Verdict: NO-GO**" in md
    assert md.index("| RED |") < md.index("| GREEN |")
    assert "input to a human decision" in md


def test_cli_roundtrip_and_gate(write, cli, tmp_path):
    files = [write("p.json", json.dumps(profile())), write("c.json", json.dumps(coa(approved_coverage=0.5))), write("d.json", json.dumps(dedupe()))]
    out = tmp_path / "o"
    code, stdout, err = cli("readiness", *files, "--out", out)
    assert code == 0 and "Verdict: NO-GO" in stdout
    assert json.loads((out / "readiness-summary.json").read_text())["verdict"] == "NO-GO"
    code, _, _ = cli("readiness", *files, "--out", out, "--fail-on-no-go")
    assert code == 3


def test_cli_errors(write, cli, tmp_path):
    code, _, err = cli("readiness", write("bad.json", "not json"), "--out", tmp_path)
    assert code == 2 and "cannot read as JSON" in err
    code, _, err = cli("readiness", write("list.json", "[1]"), "--out", tmp_path)
    assert code == 2 and "JSON object" in err
    code, _, err = cli("readiness", str(tmp_path / "missing.json"), "--out", tmp_path)
    assert code == 2 and "file not found" in err
    code, _, err = cli("readiness", write("p.json", json.dumps(profile())), "--thresholds", write("t.json", '{"x": 1}'), "--out", tmp_path)
    assert code == 2 and "Unknown threshold" in err
