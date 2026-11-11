import csv

import pytest

from erp_consol import coa
from erp_consol.csvio import read_table
from erp_consol.errors import InputError

TARGET = """account,name,type,postable
10000,Assets,asset,n
10100,Trade receivables,asset,y
10200,Bank current accounts,asset,y
10300,Plant and machinery at cost,asset,y
10310,Plant and machinery accumulated depreciation,asset,y
20100,Trade payables,liability,y
20200,Accruals,liability,y
40100,Revenue domestic,revenue,y
40200,Revenue export,revenue,y
50100,Raw materials consumed,expense,y
61100,Rent,expense,y
"""

SOURCE = """acct,title,kind
1100,Trade Debtors Control,Current Asset
1200,Bank Current Account,Bank
1300,Plant & Machinery - Cost,Fixed Asset
1310,P&M Acc Depn,Fixed Asset
2100,Trade Creditors,Current Liability
2200,Accruals,Current Liability
4100,Sales - Domestic,Sales
4200,Sales - Export,Sales
5100,Purchases - Raw Materials,Cost of Sales
6100,Premises Rent,Overhead
7000,Foundry Sand Reclamation,Cost of Sales
8000,Mystery Account,Taxation
"""


def charts(write, source=SOURCE, target=TARGET):
    s = coa.load_chart(read_table(write("s.csv", source)), {"account": "acct", "name": "title", "type": "kind"})
    t = coa.load_chart(read_table(write("t.csv", target)), {})
    return s, t


def by_code(rows):
    return {r["source_account"]: r for r in rows}


def test_type_normalisation():
    assert coa.normalise_type("Fixed Asset") == "asset"
    assert coa.normalise_type("Bank") == "asset"
    assert coa.normalise_type("Cost of Sales") == "expense"
    assert coa.normalise_type("Other Income") == "revenue"
    assert coa.normalise_type("Long Term Liability") == "liability"
    assert coa.normalise_type("Provisions and liabilities") == "liability"
    assert coa.normalise_type("Taxation") == ""
    assert coa.normalise_type("") == ""
    assert coa.normalise_type("Weird", {"weird": "equity"}) == "equity"


def test_name_normalisation_uses_synonyms():
    assert coa.normalise_account_name("Trade Debtors Control") == coa.normalise_account_name("Trade Receivables Control")
    assert coa.normalise_account_name("P&M Acc Depn") == coa.normalise_account_name("Plant and machinery accumulated depreciation")


def test_suggestions_by_type_and_name(write):
    s, t = charts(write)
    rows, exc, summary = coa.map_chart(s, t, [])
    r = by_code(rows)
    assert r["1100"]["target_account"] == "10100" and r["1100"]["status"] == "review"
    assert r["1200"]["target_account"] == "10200"
    assert r["1300"]["target_account"] == "10300"
    assert r["1310"]["target_account"] == "10310"
    assert r["2100"]["target_account"] == "20100"
    assert r["4100"]["target_account"] == "40100"
    assert r["4200"]["target_account"] == "40200"
    assert r["1100"]["confidence"] == "0.81" and "low_confidence" in r["1100"]["flags"]
    assert r["1310"]["confidence"] == "1.00" and r["1310"]["flags"] == ""
    # Names that share few words are left for a person: "Purchases - Raw Materials" vs "Raw materials consumed"
    assert r["5100"]["status"] == "unmapped" and r["6100"]["status"] == "unmapped"
    assert all(x["method"] == "suggested" for x in rows if x["target_account"])
    assert summary["approved"] == 0
    assert summary["approved_coverage"] == 0.0


def test_header_accounts_are_never_suggested(write):
    s, t = charts(write, source="acct,title,kind\n1,Assets,Fixed Asset\n")
    rows, _, _ = coa.map_chart(s, t, [])
    assert rows[0]["target_account"] != "10000"


def test_types_limit_candidates(write):
    # "Rent" must not be offered an asset account even if a name were closer
    s, t = charts(write, source="acct,title,kind\n1,Trade Receivables Rent,Overhead\n")
    rows, _, _ = coa.map_chart(s, t, [])
    assert rows[0]["target_account"] in ("", "61100")


def test_unmapped_and_unknown_type_are_reported(write):
    s, t = charts(write)
    rows, exc, summary = coa.map_chart(s, t, [])
    r = by_code(rows)
    assert r["7000"]["status"] == "unmapped"
    assert r["8000"]["status"] == "unmapped" and "type_unknown" in r["8000"]["flags"]
    issues = {(e["source_account"], e["issue"]) for e in exc}
    assert ("7000", "unmapped") in issues and ("8000", "type_unknown") in issues
    assert summary["unmapped"] == 4  # 5100, 6100, 7000 and 8000
    assert summary["suggested_for_review"] == 8


def test_manual_mapping_wins_and_is_approved(write):
    s, t = charts(write)
    rows, exc, summary = coa.map_chart(s, t, [("6100", "61100", 2), ("7000", "50100", 3)])
    r = by_code(rows)
    assert r["6100"]["method"] == "manual" and r["6100"]["status"] == "approved" and r["6100"]["confidence"] == "1.00"
    assert r["7000"]["target_account"] == "50100" and r["7000"]["status"] == "approved"
    assert summary["approved"] == 2


def test_manual_mapping_overrides_a_better_name_match(write):
    s, t = charts(write)
    rows, _, _ = coa.map_chart(s, t, [("1100", "10200", 2)])
    assert by_code(rows)["1100"]["target_account"] == "10200"


def test_manual_errors_are_flagged(write):
    s, t = charts(write)
    manual = [("1100", "99999", 2), ("9999", "10100", 3), ("1200", "10200", 4), ("1200", "10100", 5), ("5100", "10100", 6)]
    rows, exc, _ = coa.map_chart(s, t, manual)
    r = by_code(rows)
    assert r["1100"]["status"] == "unmapped" and "manual_target_unknown" in r["1100"]["flags"]
    issues = {(e["source_account"], e["issue"], e["severity"]) for e in exc}
    assert ("1100", "manual_target_unknown", "error") in issues
    assert ("9999", "manual_source_unknown", "warning") in issues
    assert ("1200", "manual_conflict", "error") in issues
    assert ("5100", "type_mismatch", "warning") in issues  # expense mapped to an asset


def test_non_postable_manual_target_flagged(write):
    s, t = charts(write)
    _, exc, _ = coa.map_chart(s, t, [("1100", "10000", 2)])
    assert any(e["issue"] == "target_not_postable" for e in exc)


def test_many_to_one(write):
    s, t = charts(write, source="acct,title,kind\n1,Bank 1,Bank\n2,Bank 2,Bank\n3,Bank 3,Bank\n")
    rows, exc, summary = coa.map_chart(s, t, [("1", "10200", 2), ("2", "10200", 3), ("3", "10200", 4)])
    assert summary["many_to_one_targets"] == 1
    assert all("many_to_one" in r["flags"] for r in rows)
    assert [e["severity"] for e in exc if e["issue"] == "many_to_one"] == ["info"]  # manual: intended


def test_many_to_one_among_suggestions_is_a_warning(write):
    s, t = charts(write, source="acct,title,kind\n1,Trade Receivables Domestic,Current Asset\n2,Trade Receivables Export,Current Asset\n")
    rows, exc, _ = coa.map_chart(s, t, [])
    assert rows[0]["target_account"] == rows[1]["target_account"] == "10100"
    assert any(e["issue"] == "many_to_one" and e["severity"] == "warning" for e in exc)


def test_ambiguity_flag(write):
    target = "account,name,type,postable\n1,Rent hall,expense,y\n2,Rent shop,expense,y\n"
    s, t = charts(write, source="acct,title,kind\n9,Rent,Overhead\n", target=target)
    rows, exc, _ = coa.map_chart(s, t, [], low=0.5, high=0.9)
    assert "ambiguous" in rows[0]["flags"]
    assert any(e["issue"] == "ambiguous" for e in exc)


def test_balance_accounts_make_unmapped_an_error(write):
    s, t = charts(write)
    rows, exc, summary = coa.map_chart(s, t, [], balance_accounts={"7000", "1100"})
    assert any(e["severity"] == "error" and e["source_account"] == "7000" for e in exc)
    assert summary["balance_accounts"] == 2 and summary["balance_accounts_not_approved"] == 2


def test_chart_validation_errors(write):
    with pytest.raises(InputError, match="already appears"):
        charts(write, source="acct,title,kind\n1,A,Bank\n1,B,Bank\n")
    with pytest.raises(InputError, match="blank"):
        charts(write, source="acct,title,kind\n1,,Bank\n")
    with pytest.raises(InputError, match="missing required column"):
        coa.load_chart(read_table(write("x.csv", "code,desc\n1,A\n")), {})


def test_load_mapping_for_use_filters_by_status(write):
    path = write("m.csv", "source_account,target_account,status\n1,10,approved\n2,20,review\n3,,unmapped\n")
    assert coa.load_mapping_for_use(path)[0] == {"1": "10"}
    assert coa.load_mapping_for_use(path, include_suggested=True)[0] == {"1": "10", "2": "20"}
    plain = write("p.csv", "source_account,target_account\n1,10\n2,20\n")
    assert coa.load_mapping_for_use(plain)[0] == {"1": "10", "2": "20"}
    with pytest.raises(InputError, match="two different targets"):
        coa.load_mapping_for_use(write("c.csv", "source_account,target_account\n1,10\n1,20\n"))


def test_manual_file_with_blank_cell_is_an_error(write):
    with pytest.raises(InputError, match="blank"):
        coa.load_manual_mapping(write("m.csv", "source_account,target_account\n1,\n"))


def test_cli_end_to_end_small(write, cli, tmp_path):
    src, tgt = write("s.csv", SOURCE), write("t.csv", TARGET)
    manual = write("m.csv", "source_account,target_account\n6100,61100\n")
    out = tmp_path / "o"
    code, stdout, err = cli("map-coa", "--source", src, "--target", tgt, "--manual", manual,
                            "--source-map", "account=acct,name=title,type=kind", "--name", "x", "--out", out)
    assert code == 0, err
    rows = list(csv.DictReader(open(out / "x.mapping.csv")))
    assert next(r for r in rows if r["source_account"] == "6100")["status"] == "approved"
    assert (out / "x.exceptions.csv").exists() and (out / "x.coa-report.md").exists()
    code, _, _ = cli("map-coa", "--source", src, "--target", tgt, "--source-map", "account=acct,name=title,type=kind",
                     "--fail-on-unapproved", "--out", out)
    assert code == 3


def test_cli_bad_confidence_and_missing_column(write, cli, tmp_path):
    src, tgt = write("s.csv", SOURCE), write("t.csv", TARGET)
    code, _, err = cli("map-coa", "--source", src, "--target", tgt, "--source-map", "account=acct,name=title,type=kind",
                       "--min-confidence", "0.9", "--high-confidence", "0.5", "--out", tmp_path)
    assert code == 2 and "Confidence limits" in err
    code, _, err = cli("map-coa", "--source", src, "--target", tgt, "--out", tmp_path)
    assert code == 2 and "missing required column" in err and "'account'" in err
