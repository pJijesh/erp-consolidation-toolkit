import json

import pytest

from erp_consol import profile
from erp_consol.csvio import read_table
from erp_consol.errors import InputError

CSV = """id,name,postcode,vat,email,created,country
1,Alpha Ltd,SW1A 1AA,GB123456789,a@alpha.example,2026-01-05,GB
2,Beta Ltd,sw1a1aa,GB12345678,b@beta.example,05/01/2026,GB
2,Gamma GmbH,70173,DE123456789,bad-email,2026-02-30,DE
3,,7017,N/A,,2026-03-01,DE
4,Delta Ltd ,M1 1AE,,d@delta.example,,GB
"""


def make(write, text=CSV):
    return read_table(write("x.csv", text))


def test_row_counts_and_missing_rates(write):
    p = profile.profile_table(make(write), key="id", required=["id", "name"])
    assert p["rows"] == 5 and p["columns"] == 7
    cols = {c["column"]: c for c in p["column_detail"]}
    assert cols["name"]["blank"] == 1 and cols["name"]["missing_rate"] == 0.2
    assert cols["vat"]["blank"] == 1 and cols["vat"]["placeholder"] == 1 and cols["vat"]["missing"] == 2
    assert cols["created"]["missing"] == 1
    assert p["required_max_missing_rate"] == 0.2


def test_duplicate_keys(write):
    p = profile.profile_table(make(write), key="id")
    assert p["key"]["duplicate_values"] == 1
    assert p["key"]["rows_with_duplicate_key"] == 2
    assert p["key_duplicate_rate"] == 0.4
    assert p["key"]["examples"] == ["2"]


def test_stray_whitespace_counted(write):
    cols = {c["column"]: c for c in profile.profile_table(make(write))["column_detail"]}
    assert cols["name"]["stray_whitespace"] == 1  # "Delta Ltd "


def test_format_checks_with_country_column(write):
    checks = [profile.parse_check("postcode=postcode"), profile.parse_check("vat=tax"), profile.parse_check("email=email")]
    p = profile.profile_table(make(write), checks=checks, country_col="country")
    by = {c["column"]: c["checks"][0] for c in p["column_detail"] if c["checks"]}
    assert by["postcode"]["checked"] == 5 and by["postcode"]["invalid"] == 1  # 7017 is not a German postcode
    assert by["postcode"]["invalid_examples"] == ["7017"]
    assert by["vat"]["checked"] == 3 and by["vat"]["invalid"] == 1  # GB12345678 is one digit short
    assert by["email"]["checked"] == 4 and by["email"]["invalid"] == 1
    assert p["format_checked_values"] == 12 and p["format_invalid_values"] == 3


def test_explicit_country_overrides_column(write):
    p = profile.profile_table(make(write), checks=[profile.parse_check("postcode=postcode:GB")], country_col="country")
    check = next(c["checks"][0] for c in p["column_detail"] if c["checks"])
    assert check["invalid"] == 2  # 70173 and 7017 are not UK postcodes


def test_date_check_reports_formats_and_invalid(write):
    chk = profile.parse_check("created=date:%Y-%m-%d|%d/%m/%Y")
    p = profile.profile_table(make(write), checks=[chk])
    d = next(c["checks"][0] for c in p["column_detail"] if c["checks"])
    assert d["checked"] == 4 and d["invalid"] == 1  # 2026-02-30 is not a date
    assert d["formats_seen"] == {"%Y-%m-%d": 2, "%d/%m/%Y": 1}
    assert d["mixed_formats"] is True


def test_examples_can_be_left_out(write):
    p = profile.profile_table(make(write), key="id", checks=[profile.parse_check("email=email")], include_examples=False)
    assert "examples" not in p["key"]
    assert "invalid_examples" not in next(c["checks"][0] for c in p["column_detail"] if c["checks"])


def test_missing_columns_named(write):
    with pytest.raises(InputError, match="'nope'"):
        profile.profile_table(make(write), key="nope")


@pytest.mark.parametrize("spec, message", [
    ("postcode", "column=type"),
    ("postcode=colour", "unknown type"),
    ("postcode=postcode:ZZ", "no postcode pattern"),
    ("ref=regex", "needs a pattern"),
    ("ref=regex:[", "invalid regular expression"),
])
def test_bad_check_specs(spec, message):
    with pytest.raises(InputError, match=message):
        profile.parse_check(spec)


def test_identical_rows(write):
    p = profile.profile_table(make(write, "a,b\n1,2\n1,2\n3,4\n"))
    assert p["identical_rows"] == 1


def test_markdown_pipe_in_value_does_not_break_table(write):
    t = make(write, "id,ref\n1,a|b\n")
    p = profile.profile_table(t, checks=[profile.parse_check("ref=regex:^x$")])
    md = profile.render_markdown(p)
    assert "a\\|b" in md


def test_cli_writes_markdown_and_json(write, cli, tmp_path):
    path = write("customers.csv", CSV)
    code, out, err = cli("profile", path, "--key", "id", "--required", "id,name", "--check", "email=email", "--out", tmp_path / "o")
    assert code == 0, err
    data = json.loads((tmp_path / "o" / "customers.profile-summary.json").read_text())
    assert data["kind"] == "profile" and data["rows"] == 5 and data["name"] == "customers"
    assert (tmp_path / "o" / "customers.profile-report.md").read_text().startswith("# Data profile: customers.csv")


def test_cli_config_file_and_errors(write, cli, tmp_path):
    path = write("c.csv", CSV)
    cfg = write("cfg.json", json.dumps({"key": "id", "required": ["name"], "checks": {"email": "email"}}))
    code, out, err = cli("profile", path, "--config", cfg, "--out", tmp_path / "o")
    assert code == 0, err
    code, out, err = cli("profile", path, "--key", "missing", "--out", tmp_path / "o")
    assert code == 2 and "missing required column" in err
    code, out, err = cli("profile", write("empty.csv", ""), "--out", tmp_path / "o")
    assert code == 2 and "is empty" in err
    code, out, err = cli("profile", str(tmp_path / "absent.csv"), "--out", tmp_path / "o")
    assert code == 2 and "file not found" in err
