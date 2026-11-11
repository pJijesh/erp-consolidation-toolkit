import pytest

from erp_consol.csvio import parse_pairs, read_table
from erp_consol.errors import InputError


def test_reads_simple_csv(write):
    t = read_table(write("a.csv", "id,name\n1,Alpha\n2,Beta\n"))
    assert t.columns == ["id", "name"]
    assert t.rows[1] == {"id": "2", "name": "Beta"}
    assert t.lines == [2, 3]
    assert t.encoding == "utf-8"
    assert t.delimiter == ","


def test_detects_semicolon_and_tab(write):
    assert read_table(write("a.csv", "id;name\n1;Alpha\n")).delimiter == ";"
    assert read_table(write("b.csv", "id\tname\n1\tAlpha\n")).delimiter == "\t"


def test_utf8_bom_is_removed(write):
    t = read_table(write("a.csv", b"\xef\xbb\xbfid,name\n1,Alpha\n"))
    assert t.columns == ["id", "name"]
    assert t.encoding == "utf-8-sig"


def test_windows_1252_fallback_warns(write):
    t = read_table(write("a.csv", "id,name\n1,Müller\n".encode("cp1252")))
    assert t.rows[0]["name"] == "Müller"
    assert t.encoding == "cp1252"
    assert any("Windows-1252" in w for w in t.warnings)


def test_explicit_encoding_is_respected(write):
    t = read_table(write("a.csv", "id,name\n1,Café\n".encode("latin-1")), encoding="latin-1")
    assert t.rows[0]["name"] == "Café"
    assert t.warnings == []


def test_unknown_encoding_name_is_an_input_error(write):
    with pytest.raises(InputError, match="cannot decode"):
        read_table(write("a.csv", "id\n1\n"), encoding="no-such-codec")


def test_undecodable_bytes_are_an_input_error(write):
    with pytest.raises(InputError, match="not valid UTF-8 or Windows-1252"):
        read_table(write("a.csv", b"id,name\n1,\x81\x8d\n"))


def test_empty_file(write):
    with pytest.raises(InputError, match="is empty"):
        read_table(write("a.csv", ""))
    with pytest.raises(InputError, match="is empty"):
        read_table(write("b.csv", "   \n\n"))


def test_header_only(write):
    with pytest.raises(InputError, match="no data rows"):
        read_table(write("a.csv", "id,name\n"))
    assert read_table(write("b.csv", "id,name\n"), allow_empty=True).rows == []


def test_excel_workbook_is_recognised(write):
    with pytest.raises(InputError, match="Excel"):
        read_table(write("a.csv", b"PK\x03\x04\x00\x00binary"))


def test_nul_bytes_rejected(write):
    with pytest.raises(InputError, match="NUL"):
        read_table(write("a.csv", b"id,name\x00\n1,2\n"))


def test_missing_file_and_directory(tmp_path):
    with pytest.raises(InputError, match="file not found"):
        read_table(str(tmp_path / "nope.csv"))
    with pytest.raises(InputError, match="folder"):
        read_table(str(tmp_path))


def test_duplicate_and_blank_headers(write):
    with pytest.raises(InputError, match="duplicate column"):
        read_table(write("a.csv", "id,ID\n1,2\n"))
    with pytest.raises(InputError, match="empty column name"):
        read_table(write("b.csv", "id,\n1,2\n"))


def test_wrong_field_count_reports_line_numbers(write):
    with pytest.raises(InputError, match=r"line 3"):
        read_table(write("a.csv", "id,name\n1,Alpha\n2,Beta,extra\n"))


def test_blank_rows_ignored_with_warning(write):
    t = read_table(write("a.csv", "id,name\n1,Alpha\n,\n\n2,Beta\n"))
    assert len(t.rows) == 2
    assert any("blank row" in w for w in t.warnings)


def test_quoted_fields_with_commas_and_newlines(write):
    t = read_table(write("a.csv", 'id,name\n1,"Smith, Jones"\n2,"two\nlines"\n'))
    assert t.rows[0]["name"] == "Smith, Jones"
    assert t.rows[1]["name"] == "two\nlines"


def test_resolve_names_every_missing_column(write):
    t = read_table(write("a.csv", "id,name\n1,Alpha\n"))
    with pytest.raises(InputError) as exc:
        t.resolve(["id", "tax", "postcode"])
    msg = str(exc.value)
    assert "'tax'" in msg and "'postcode'" in msg and "Columns found: id, name" in msg


def test_find_column_ignores_case(write):
    t = read_table(write("a.csv", "ID,Name\n1,Alpha\n"))
    assert t.find_column("id") == "ID"
    assert t.find_column("missing") is None


def test_parse_pairs():
    assert parse_pairs("id=cust_id, name=cust_name", ["id", "name"], "--a-map") == {"id": "cust_id", "name": "cust_name"}
    assert parse_pairs(None, ["id"], "--a-map") == {}
    with pytest.raises(InputError, match="unknown key"):
        parse_pairs("bogus=x", ["id"], "--a-map")
    with pytest.raises(InputError, match="key=column"):
        parse_pairs("id", ["id"], "--a-map")
