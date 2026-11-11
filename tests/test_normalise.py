from decimal import Decimal

import pytest

from erp_consol import normalise as n
from erp_consol.errors import InputError


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("Brightwell Engineering Ltd", "brightwell engineering"),
        ("BRIGHTWELL ENGINEERING LIMITED", "brightwell engineering"),
        ("Brightwell Engineering Ltd.", "brightwell engineering"),
        ("Müller Pumpen GmbH & Co. KG", "mueller pumpen"),
        ("Mueller Pumpen GmbH", "mueller pumpen"),
        ("Smith & Sons Inc.", "smith and sons"),
        ("The Foundry Company Limited", "foundry"),
        ("Limited", "limited"),  # never strip a name down to nothing
        ("Acme Intl Mfg Ltd", "acme international manufacturing"),
        ("  Double   Spaced  Ltd ", "double spaced"),
    ],
)
def test_normalise_name(raw, expected):
    assert n.normalise_name(raw) == expected


def test_normalise_name_extra_suffix():
    assert n.normalise_name("Acme Holdings", frozenset({"holdings"})) == "acme"


def test_similarity_is_symmetric_and_bounded():
    a, b = "pump systems brelden", "brelden pump systems"
    assert n.similarity(a, b) == n.similarity(b, a)
    assert n.similarity(a, b) == 1.0  # same words, different order
    assert n.similarity("abc", "") == 0.0
    assert 0.0 < n.similarity("valve body", "valve bodies") < 1.0


@pytest.mark.parametrize(
    "raw, country, expected",
    [
        ("sw1a 1aa", "GB", "SW1A1AA"),
        ("SW1A  1AA", None, "SW1A1AA"),
        ("4109", "DE", "04109"),  # leading zero lost in a spreadsheet
        ("4109", "FR", "4109"),
        ("", "GB", ""),
    ],
)
def test_normalise_postcode(raw, country, expected):
    assert n.normalise_postcode(raw, country) == expected


@pytest.mark.parametrize(
    "raw, expected",
    [("GB 123 4567 89", "123456789"), ("gb123456789", "123456789"), ("123456789", "123456789"),
     ("DE 123.456.789", "123456789"), ("NL123456789B01", "123456789B01"), ("", "")],
)
def test_normalise_tax(raw, expected):
    assert n.normalise_tax(raw) == expected


def test_valid_postcode_by_country():
    assert n.valid_postcode("SW1A 1AA", "GB")
    assert n.valid_postcode("M1 1AE", "United Kingdom")
    assert n.valid_postcode("EC1A 1BB", "GB")
    assert not n.valid_postcode("SW1A 1A", "GB")
    assert n.valid_postcode("70173", "DE")
    assert not n.valid_postcode("7017", "DE")
    assert n.valid_postcode("1234 AB", "NL")
    assert n.valid_postcode("AB12 3CD", None)  # unknown country falls back to a loose pattern


def test_valid_tax_by_country():
    assert n.valid_tax("GB 123 4567 89", "GB")
    assert n.valid_tax("GB123456789012", "GB")
    assert n.valid_tax("GBGD123", "GB")
    assert not n.valid_tax("GB12345678", "GB")
    assert n.valid_tax("DE123456789", "DE")
    assert not n.valid_tax("DE12345678", "DE")
    assert n.valid_tax("NL123456789B01", "NL")
    assert n.valid_tax("FRAB123456789", "FR")


def test_valid_email():
    assert n.valid_email("a.b@example.co.uk")
    assert not n.valid_email("a.b.example.co.uk")
    assert not n.valid_email("a@b")
    assert not n.valid_email("a@b.com ")  # trailing space


def test_email_domain_ignores_free_mail():
    assert n.email_domain("sales@brightwell.example") == "brightwell.example"
    assert n.email_domain("someone@gmail.com") == ""
    assert n.email_domain("not an email") == ""


@pytest.mark.parametrize(
    "raw, expected",
    [("MC-10442", "MC10442"), ("mc 10442-b", "MC10442B"), ("MC-0010442", "MC10442"), ("MC-010442", "MC10442"),
     ("100", "100"), ("0", "0"), ("", "")],
)
def test_normalise_part_number(raw, expected):
    assert n.normalise_part_number(raw) == expected


def test_part_number_relation():
    assert n.part_number_relation("MC10442", "MC10442") == "equal"
    assert n.part_number_relation("MC10442", "MC10442B") == "revision"
    assert n.part_number_relation("MC10442B", "MC10442") == "revision"
    assert n.part_number_relation("MC10442", "MC104420") == "none"
    assert n.part_number_relation("MC10442", "MC10443") == "none"
    assert n.part_number_relation("", "MC10443") == "none"


def test_normalise_uom():
    assert n.normalise_uom("ST") == "EA"
    assert n.normalise_uom("Stück") == "EA"
    assert n.normalise_uom("MTR") == "M"
    assert n.normalise_uom("CTN") == "CTN"
    assert n.normalise_uom("CTN", {"CTN": "BOX"}) == "BOX"
    assert n.normalise_uom("") == ""


def test_normalise_description_expands_abbreviations():
    assert n.normalise_description("Gate valve DN 50 S/S") == "gate valve dn 50 stainless steel"
    assert n.normalise_description("IMPELLER DI") == "impeller ductile iron"


@pytest.mark.parametrize(
    "raw, decimal_comma, expected",
    [("1234.56", False, "1234.56"), ("1,234.56", False, "1234.56"), ("(100.00)", False, "-100.00"),
     ("100.00-", False, "-100.00"), ("-5", False, "-5"), ("", False, "0"), ("£12.50", False, "12.50"),
     ("1.234,56", True, "1234.56"), ("0,05", True, "0.05")],
)
def test_parse_amount(raw, decimal_comma, expected):
    assert n.parse_amount(raw, decimal_comma) == Decimal(expected)


@pytest.mark.parametrize("raw, decimal_comma", [("12abc", False), ("1.234,56", False), ("1,5x", True)])
def test_parse_amount_rejects_bad_values(raw, decimal_comma):
    with pytest.raises(InputError):
        n.parse_amount(raw, decimal_comma)
