import csv
import json

import pytest

from erp_consol import decision
from erp_consol.errors import InputError

ITEMS = decision.load_criteria(decision.default_criteria_path())
CRITERIA = [i for i in ITEMS if i.kind == "criterion"]
GATES = [i for i in ITEMS if i.kind == "gate"]


def values(score=3, gates="no", **overrides):
    v = {i.id: str(score) for i in CRITERIA}
    v.update({g.id: gates for g in GATES})
    v.update({k: str(x) if k.startswith("C") else x for k, x in overrides.items()})
    return v


def test_criteria_file_shape():
    assert len(CRITERIA) == 13 and len(GATES) == 4
    assert {i.axis for i in CRITERIA} == {"case", "ability"}
    assert {g.effect for g in GATES} == {"defer", "cap_partial"}
    assert sum(i.weight for i in CRITERIA if i.axis == "case") == 13
    assert sum(i.weight for i in CRITERIA if i.axis == "ability") == 16
    for i in CRITERIA:
        assert i.question and all(i.anchors.values()), i.id


def test_axis_score_arithmetic():
    assert decision.axis_score(ITEMS, values(1), "case") == 0.0
    assert decision.axis_score(ITEMS, values(5), "case") == 100.0
    assert decision.axis_score(ITEMS, values(3), "case") == 50.0
    # only the heaviest case criteria at 5: C01 (3) + C02 (3) of 13, the rest at 1
    v = values(1, C01=5, C02=5)
    assert decision.axis_score(ITEMS, v, "case") == round(100 * 6 / 13, 1)


def test_outcome_bands():
    assert decision.decide(ITEMS, values(5))["outcome"] == "CONSOLIDATE"
    assert decision.decide(ITEMS, values(3))["outcome"] == "PARTIALLY INTEGRATE"
    assert decision.decide(ITEMS, values(1))["outcome"] == "KEEP SEPARATE"


def test_strong_case_with_weak_delivery_is_partial_not_consolidate():
    v = values(5)
    for i in CRITERIA:
        if i.axis == "ability":
            v[i.id] = "2"
    r = decision.decide(ITEMS, v)
    assert r["case_score"] == 100.0 and r["ability_score"] == 25.0
    assert r["outcome"] == "PARTIALLY INTEGRATE" and "ability to deliver" in r["reasons"][0]


def test_boundaries():
    # Start with every case criterion at 1, ability criteria at 5, then raise some case criteria.
    v = values(5)
    for i in CRITERIA:
        if i.axis == "case":
            v[i.id] = "1"
    v.update({"C01": "5", "C02": "5", "C03": "5", "C04": "3"})  # weights 3+3+2+2: (3*4+3*4+2*4+2*2)/52 = 36/52 = 69.2
    assert decision.axis_score(ITEMS, v, "case") == 69.2
    assert decision.decide(ITEMS, v)["outcome"] == "CONSOLIDATE"
    v["C04"] = "1"  # 32/52 = 61.5
    assert decision.axis_score(ITEMS, v, "case") == 61.5
    assert decision.decide(ITEMS, v)["outcome"] == "PARTIALLY INTEGRATE"


def test_defer_gate_overrides_everything():
    r = decision.decide(ITEMS, values(5, G02="yes"))
    assert r["outcome"] == "DEFER" and r["gates_hit"] == ["G02"]
    assert decision.decide(ITEMS, values(5, G03="yes"))["outcome"] == "DEFER"


def test_cap_gate_limits_to_partial():
    r = decision.decide(ITEMS, values(5, G01="yes"))
    assert r["outcome"] == "PARTIALLY INTEGRATE" and any("Capped" in x for x in r["reasons"])
    assert decision.decide(ITEMS, values(5, G04="yes"))["outcome"] == "PARTIALLY INTEGRATE"
    # a cap gate does not change a lower outcome but is still mentioned
    r = decision.decide(ITEMS, values(1, G01="yes"))
    assert r["outcome"] == "KEEP SEPARATE" and any("would cap" in x for x in r["reasons"])


def test_sensitivity_finds_single_point_flips():
    v = values(1, C01=5, C02=5, C03=5, C04=3)  # case 69.2, ability 0: partial
    for i in CRITERIA:
        if i.axis == "ability":
            v[i.id] = "4"  # ability 75
    base = decision.decide(ITEMS, v)["outcome"]
    assert base == "CONSOLIDATE"
    flips = decision.sensitivity(ITEMS, v, base)
    # lowering C04 from 3 to 2 gives 34/52 = 65.4 (still consolidate); lowering C01 from 5 to 4 gives 33/52 = 63.5
    assert {f["id"] for f in flips if f["from"] == 5 and f["to"] == 4} >= {"C01", "C02"}
    assert all(f["outcome"] != base for f in flips)


def test_full_result_lists_weak_criteria_in_weight_order():
    r = decision.full_result(ITEMS, values(3, C07=1, C13=2, C02=2), {}, [])
    assert [w["id"] for w in r["weak_criteria"]] == ["C02", "C07", "C13"]


def test_score_file_validation(write):
    ok = "id,value,evidence\n" + "\n".join(f"{i.id},{'3' if i.kind == 'criterion' else 'no'},because" for i in ITEMS) + "\n"
    vals, ev, warnings = decision.load_scores(write("ok.csv", ok), ITEMS)
    assert vals["C01"] == "3" and vals["G01"] == "no" and ev["C01"] == "because" and warnings == []
    with pytest.raises(InputError, match="no value for G04"):
        decision.load_scores(write("m.csv", ok.replace("G04,no,because\n", "")), ITEMS)
    with pytest.raises(InputError, match="needs a score from 1 to 5"):
        decision.load_scores(write("r.csv", ok.replace("C01,3", "C01,6")), ITEMS)
    with pytest.raises(InputError, match="needs yes or no"):
        decision.load_scores(write("g.csv", ok.replace("G01,no", "G01,maybe")), ITEMS)
    with pytest.raises(InputError, match="unknown id 'C99'"):
        decision.load_scores(write("u.csv", ok + "C99,3,x\n"), ITEMS)
    with pytest.raises(InputError, match="appears twice"):
        decision.load_scores(write("d.csv", ok + "C01,4,x\n"), ITEMS)


def test_missing_evidence_is_a_warning_not_an_error(write):
    ok = "id,value,evidence\n" + "\n".join(f"{i.id},{'3' if i.kind == 'criterion' else 'no'}," for i in ITEMS) + "\n"
    _, _, warnings = decision.load_scores(write("ok.csv", ok), ITEMS)
    assert len(warnings) == 17


def test_criteria_file_errors(write):
    head = "id,kind,axis,name,weight,question,score_1,score_3,score_5,effect\n"
    with pytest.raises(InputError, match="kind must be"):
        decision.load_criteria(write("a.csv", head + "C1,thing,case,N,1,Q,a,b,c,\n"))
    with pytest.raises(InputError, match="axis must be"):
        decision.load_criteria(write("b.csv", head + "C1,criterion,other,N,1,Q,a,b,c,\n"))
    with pytest.raises(InputError, match="weight must be a whole number"):
        decision.load_criteria(write("c.csv", head + "C1,criterion,case,N,x,Q,a,b,c,\n"))
    with pytest.raises(InputError, match="effect"):
        decision.load_criteria(write("d.csv", head + "G1,gate,,N,0,Q,,,,boom\n"))
    with pytest.raises(InputError, match="duplicate id"):
        decision.load_criteria(write("e.csv", head + "C1,criterion,case,N,1,Q,a,b,c,\nC1,criterion,case,N,1,Q,a,b,c,\n"))


def test_cli_roundtrip(cli, root, tmp_path):
    code, out, err = cli("decide", "--scores", f"{root}/decision/examples/two-manufacturers.csv", "--out", tmp_path)
    assert code == 0, err
    assert "PARTIALLY INTEGRATE (case 57.7, ability 29.7)" in out
    data = json.loads((tmp_path / "two-manufacturers.decision-summary.json").read_text())
    assert data["outcome"] == "PARTIALLY INTEGRATE" and data["gates_hit"] == ["G04"]


def test_worked_examples_reach_the_documented_outcomes(cli, root, tmp_path):
    expected = {"two-manufacturers": "PARTIALLY INTEGRATE", "two-uk-distributors": "CONSOLIDATE",
                "different-regulated-businesses": "KEEP SEPARATE"}
    for name, outcome in expected.items():
        code, out, err = cli("decide", "--scores", f"{root}/decision/examples/{name}.csv", "--out", tmp_path)
        assert code == 0, err
        assert json.loads((tmp_path / f"{name}.decision-summary.json").read_text())["outcome"] == outcome


def test_cli_missing_scores_file(cli, tmp_path):
    code, _, err = cli("decide", "--scores", str(tmp_path / "none.csv"), "--out", tmp_path)
    assert code == 2 and "file not found" in err
