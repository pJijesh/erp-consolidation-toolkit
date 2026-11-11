import csv
import json
from decimal import Decimal

import pytest

from erp_consol import coa, reconcile
from erp_consol.csvio import read_table
from erp_consol.errors import InputError

SRC = """acct,name,kind
100,Bank,Bank
110,Debtors,Current Asset
200,Creditors,Current Liability
300,Share capital,Equity
400,Sales,Sales
500,Materials,Cost of Sales
900,Odd account,Taxation
"""
TGT = """account,name,type
1000,Cash and bank,asset
1100,Trade receivables,asset
2000,Trade payables,liability
3000,Share capital,equity
4000,Revenue,revenue
5000,Cost of sales,expense
5100,Inventory,asset
"""
TB = """period,acct,debit,credit
2026-01,100,500.00,
2026-01,110,300.00,
2026-01,200,,200.00
2026-01,300,,400.00
2026-01,400,,1000.00
2026-01,500,800.00,
2026-02,100,"1,500.00",
2026-02,110,300.00,
2026-02,200,,200.00
2026-02,300,,400.00
2026-02,400,,2000.00
2026-02,500,800.00,
"""
FULL = {"100": "1000", "110": "1100", "200": "2000", "300": "3000", "400": "4000", "500": "5000"}


def setup(write, tb=TB):
    src = coa.load_chart(read_table(write("s.csv", SRC)), {"account": "acct", "name": "name", "type": "kind"})
    tgt = coa.load_chart(read_table(write("t.csv", TGT)), {})
    return src, tgt, reconcile.load_trial_balance(read_table(write("tb.csv", tb)), {"account": "acct"})


def run(write, mapping, **kw):
    src, tgt, tb = setup(write)
    return reconcile.reconcile(tb, mapping, src, tgt, kw.pop("tolerance", Decimal("0.01")), **kw)


def test_loads_debit_credit_and_signs(write):
    _, _, tb = setup(write)
    assert tb.periods == ["2026-01", "2026-02"]
    assert tb.net[("2026-01", "100")] == Decimal("500.00")
    assert tb.net[("2026-01", "200")] == Decimal("-200.00")
    assert tb.net[("2026-02", "100")] == Decimal("1500.00")  # thousands separator read correctly


def test_balance_column_and_decimal_comma(write):
    tb = reconcile.load_trial_balance(read_table(write("t.csv", "period;acct;balance\n2026-01;100;1.234,50\n2026-01;200;-1.234,50\n")), {"account": "acct"}, True)
    assert tb.net[("2026-01", "100")] == Decimal("1234.50")
    assert tb.net[("2026-01", "200")] == Decimal("-1234.50")


def test_clean_mapping_reconciles(write):
    summary, diffs = run(write, FULL)
    jan = summary["periods_detail"][0]
    assert jan["source_net"] == "0.00" and jan["mapped_net"] == "0.00" and jan["unmapped_net"] == "0.00"
    assert jan["source_debit"] == "1600.00" and jan["source_credit"] == "1600.00"
    assert jan["status"] == "OK"
    # February: 1500 + 300 + 800 debit against 200 + 400 + 2000 credit
    feb = summary["periods_detail"][1]
    assert feb["source_net"] == "0.00"
    assert summary["periods_ok"] == 2 and diffs == []


def test_unmapped_balance_is_reported_with_amount(write):
    mapping = dict(FULL)
    del mapping["110"]
    summary, diffs = run(write, mapping)
    jan = summary["periods_detail"][0]
    assert jan["unmapped_net"] == "300.00" and jan["mapped_net"] == "-300.00"
    assert jan["unmapped_accounts_with_balance"] == 1 and jan["status"] == "DIFFERENCES"
    assert any(d[0] == "unmapped_balance" and d[2] == "110" and d[5] == "-300.00" for d in diffs)
    assert summary["unmapped_accounts_with_balance"] == 1


def test_unmapped_inside_tolerance_is_not_a_difference(write):
    tb = TB.replace("2026-01,110,300.00,", "2026-01,110,0.005,").replace("2026-01,100,500.00,", "2026-01,100,799.995,")
    src, tgt, t = setup(write, tb)
    mapping = {k: v for k, v in FULL.items() if k != "110"}
    summary, diffs = reconcile.reconcile(t, mapping, src, tgt, Decimal("0.01"))
    assert summary["periods_detail"][0]["status"] == "OK"
    assert [d for d in diffs if d[1] == "2026-01"] == []


def test_reclassification_between_classes(write):
    mapping = dict(FULL, **{"500": "5100"})  # an expense account mapped to an inventory asset
    summary, diffs = run(write, mapping)
    jan = summary["periods_detail"][0]["class_detail"]
    assert jan["expense"] == {"before": "800.00", "unmapped": "0.00", "after": "0.00", "reclassified": "-800.00"}
    assert jan["asset"]["reclassified"] == "800.00"
    assert {d[0] for d in diffs} == {"reclassification"}
    assert jan["revenue"]["reclassified"] == "0.00"
    summary2, diffs2 = run(write, mapping, allow_reclassification=True)
    assert summary2["periods_ok"] == 2 and {d[0] for d in diffs2} == {"reclassification_accepted"}


def test_unknown_source_type_becomes_unclassified(write):
    tb = TB + "2026-01,900,10.00,\n2026-01,100,,10.00\n"
    src, tgt, t = setup(write, tb)
    summary, diffs = reconcile.reconcile(t, dict(FULL, **{"900": "5000"}), src, tgt, Decimal("0.01"))
    jan = summary["periods_detail"][0]["class_detail"]
    assert jan["unclassified"]["before"] == "10.00" and jan["unclassified"]["reclassified"] == "-10.00"
    assert jan["expense"]["reclassified"] == "10.00"


def test_source_out_of_balance_detected(write):
    tb = TB.replace("2026-01,400,,1000.00", "2026-01,400,,900.00")
    src, tgt, t = setup(write, tb)
    summary, diffs = reconcile.reconcile(t, FULL, src, tgt, Decimal("0.01"))
    assert summary["periods_detail"][0]["flags"] == "source_out_of_balance"
    assert any(d[0] == "source_out_of_balance" and d[5] == "100.00" for d in diffs)


def test_target_trial_balance_comparison(write):
    target_tb = reconcile.load_trial_balance(read_table(write("lt.csv", """period,account,debit,credit
2026-01,1000,500.00,
2026-01,1100,300.03,
2026-01,2000,,200.00
2026-01,3000,,400.00
2026-01,4000,,1000.00
2026-01,5000,800.00,
2026-02,1000,1500.00,
2026-02,1100,300.00,
2026-02,2000,,200.00
2026-02,3000,,400.00
2026-02,4000,,1900.00
""")), {"account": "account"})
    summary, diffs = run(write, FULL, target_tb=target_tb, tolerance=Decimal("0.05"))
    rows = {(d[1], d[2]): d for d in diffs}
    assert ("2026-01", "1100") not in rows  # 0.03 is inside the 0.05 tolerance
    assert rows[("2026-02", "4000")][5] == "100.00"  # revenue loaded 100 higher than mapped
    assert rows[("2026-02", "5000")][5] == "-800.00"  # a missing account
    assert summary["target_tb_differences"] == 2
    assert summary["periods_detail"][0]["status"] == "OK"
    assert summary["periods_detail"][1]["target_tb_differences"] == 2


def test_tolerance_boundary(write):
    tb = TB + "2026-01,110,0.01,\n2026-01,200,,0.01\n"
    src, tgt, t = setup(write, tb)
    mapping = {k: v for k, v in FULL.items() if k != "110"}
    s, _ = reconcile.reconcile(t, mapping, src, tgt, Decimal("300.01"))
    assert s["periods_detail"][0]["status"] == "OK"  # a difference equal to the tolerance is accepted
    s, _ = reconcile.reconcile(t, mapping, src, tgt, Decimal("299.99"))
    assert s["periods_detail"][0]["status"] == "DIFFERENCES"


def test_mapping_to_unknown_target_is_an_error(write):
    with pytest.raises(InputError, match="not in the target chart"):
        run(write, dict(FULL, **{"100": "9999"}))


def test_trial_balance_errors(write):
    with pytest.raises(InputError, match="debit.*credit.*balance"):
        reconcile.load_trial_balance(read_table(write("a.csv", "period,acct,amount\n2026-01,1,5\n")), {"account": "acct"})
    with pytest.raises(InputError, match="line 2.*not a number"):
        reconcile.load_trial_balance(read_table(write("b.csv", "period,account,debit,credit\n2026-01,1,abc,\n")))
    with pytest.raises(InputError, match="blank period or account"):
        reconcile.load_trial_balance(read_table(write("c.csv", "period,account,debit,credit\n,1,5,\n")))
    with pytest.raises(InputError, match="missing required column"):
        reconcile.load_trial_balance(read_table(write("d.csv", "month,account,debit,credit\n1,1,5,\n")))


def test_repeated_lines_are_added_and_warned(write):
    tb = reconcile.load_trial_balance(read_table(write("a.csv", "period,account,debit,credit\n2026-01,1,5,\n2026-01,1,7,\n")))
    assert tb.net[("2026-01", "1")] == Decimal("12") and tb.warnings


def test_cli_end_to_end(write, cli, tmp_path):
    src, tgt, tb = write("s.csv", SRC), write("t.csv", TGT), write("tb.csv", TB)
    mapping = write("m.csv", "source_account,target_account\n" + "\n".join(f"{k},{v}" for k, v in FULL.items()) + "\n")
    out = tmp_path / "o"
    args = ["reconcile", "--tb", tb, "--mapping", mapping, "--source-coa", src, "--target-coa", tgt,
            "--source-map", "account=acct,type=kind", "--tb-map", "account=acct", "--name", "x", "--out", out]
    code, stdout, err = cli(*args, "--fail-on-difference")
    assert code == 0, err
    summary = json.loads((out / "x.reconcile-summary.json").read_text())
    assert summary["periods"] == 2 and summary["periods_with_differences"] == 0
    rows = list(csv.DictReader(open(out / "x.reconcile-by-period.csv")))
    assert [r["status"] for r in rows] == ["OK", "OK"]
    partial = write("p.csv", "source_account,target_account\n100,1000\n")
    args[args.index(mapping)] = partial
    code, _, _ = cli(*args, "--fail-on-difference")
    assert code == 3


def test_cli_bad_tolerance(write, cli, tmp_path):
    code, _, err = cli("reconcile", "--tb", write("tb.csv", TB), "--mapping", write("m.csv", "source_account,target_account\n1,2\n"),
                       "--source-coa", write("s.csv", SRC), "--target-coa", write("t.csv", TGT), "--tolerance", "abc", "--out", tmp_path)
    assert code == 2 and "not a number" in err
    code, _, err = cli("reconcile", "--tb", write("tb.csv", TB), "--mapping", write("m.csv", "source_account,target_account\n1,2\n"),
                       "--source-coa", write("s.csv", SRC), "--target-coa", write("t.csv", TGT), "--tolerance", "-1", "--out", tmp_path)
    assert code == 2 and "negative" in err
