"""Normalisation and format helpers.

Everything here is a pure function, so the behaviour is easy to test and the
scoring models built on top of it are reproducible.
"""

from __future__ import annotations

import re
import unicodedata
from datetime import datetime
from decimal import Decimal, InvalidOperation
from difflib import SequenceMatcher

from .errors import InputError

# ---------------------------------------------------------------------------
# Text folding and names
# ---------------------------------------------------------------------------

_TRANSLIT = {"ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "æ": "ae", "ø": "o", "œ": "oe", "å": "a"}

# Legal form words removed from the end of a party name. This is a convenience
# list, not a legal reference: extend it with --legal-suffixes if your estate needs more.
LEGAL_SUFFIXES = frozenset(
    {
        "ltd", "limited", "plc", "llp", "lp", "llc", "inc", "incorporated", "corp",
        "corporation", "co", "company", "gmbh", "mbh", "ag", "kg", "ohg", "ug", "bv",
        "nv", "sa", "sas", "sarl", "srl", "spa", "ab", "oy", "pty", "pte", "and",
    }
)

NAME_ABBREVIATIONS = {
    "eng": "engineering",
    "engg": "engineering",
    "intl": "international",
    "int": "international",
    "mfg": "manufacturing",
    "svcs": "services",
    "svc": "services",
    "grp": "group",
}


def fold_text(value: str) -> str:
    """Lower case, transliterate German style umlauts, and strip other accents."""
    value = value.lower()
    for src, dst in _TRANSLIT.items():
        value = value.replace(src, dst)
    value = unicodedata.normalize("NFKD", value)
    return "".join(ch for ch in value if not unicodedata.combining(ch))


def _tokens(value: str) -> list[str]:
    value = fold_text(value).replace("&", " and ")
    value = value.replace(".", "").replace("'", "")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return value.split()


def normalise_name(value: str, extra_suffixes: frozenset[str] = frozenset()) -> str:
    """Normalise a party name: fold, expand abbreviations, drop trailing legal forms.

    The legal form is removed only from the end of the name, and never if that
    would leave nothing, so a company called just "Limited" keeps its name.
    """
    tokens = [NAME_ABBREVIATIONS.get(t, t) for t in _tokens(value or "")]
    if tokens and tokens[0] == "the" and len(tokens) > 1:
        tokens = tokens[1:]
    suffixes = LEGAL_SUFFIXES | extra_suffixes
    trimmed = list(tokens)
    while len(trimmed) > 1 and trimmed[-1] in suffixes:
        trimmed.pop()
    return " ".join(trimmed)


def similarity(a: str, b: str) -> float:
    """Symmetric text similarity in [0, 1] built on difflib.

    Takes the better of a character ratio on the text as written and on the
    text with words sorted, so "Pump Systems Brelden" scores well against
    "Brelden Pump Systems". Arguments are ordered before comparing because
    SequenceMatcher can give slightly different answers in each direction.
    """
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    x, y = (a, b) if a <= b else (b, a)
    direct = SequenceMatcher(None, x, y, autojunk=False).ratio()
    sx, sy = " ".join(sorted(x.split())), " ".join(sorted(y.split()))
    sorted_ratio = SequenceMatcher(None, sx, sy, autojunk=False).ratio() if (sx, sy) != (x, y) else direct
    return max(direct, sorted_ratio)


# ---------------------------------------------------------------------------
# Countries, postcodes, tax numbers, email
# ---------------------------------------------------------------------------

COUNTRY_ALIASES = {
    "gb": "GB", "uk": "GB", "gbr": "GB", "united kingdom": "GB", "great britain": "GB",
    "england": "GB", "scotland": "GB", "wales": "GB",
    "de": "DE", "deu": "DE", "germany": "DE", "deutschland": "DE",
    "nl": "NL", "nld": "NL", "netherlands": "NL", "holland": "NL",
    "fr": "FR", "fra": "FR", "france": "FR",
    "us": "US", "usa": "US", "united states": "US",
}


def normalise_country(value: str | None) -> str:
    if not value:
        return ""
    key = value.strip().lower()
    return COUNTRY_ALIASES.get(key, value.strip().upper())


def normalise_postcode(value: str | None, country: str | None = None) -> str:
    """Upper case, strip spaces and hyphens. Restores the leading zero German codes lose in spreadsheets."""
    if not value:
        return ""
    pc = re.sub(r"[\s\-]+", "", value.upper())
    if normalise_country(country) == "DE" and pc.isdigit() and len(pc) == 4:
        pc = "0" + pc
    return pc


def normalise_tax(value: str | None) -> str:
    """Upper case alphanumerics only, with a two letter country prefix removed.

    Removing the prefix lets "GB123456789" match "123456789". The check digits
    are not validated.
    """
    if not value:
        return ""
    tax = re.sub(r"[^A-Za-z0-9]", "", value).upper()
    if len(tax) > 3 and tax[:2].isalpha() and tax[2].isdigit():
        tax = tax[2:]
    return tax


_FREE_MAIL = frozenset(
    {"gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "hotmail.co.uk", "yahoo.com",
     "yahoo.co.uk", "live.com", "icloud.com", "aol.com", "gmx.de", "gmx.net", "web.de", "t-online.de"}
)


def email_domain(value: str | None) -> str:
    """The domain of a business email address, or empty for blanks and free-mail providers."""
    if not value or "@" not in value:
        return ""
    domain = value.strip().rsplit("@", 1)[1].lower()
    return "" if domain in _FREE_MAIL else domain


POSTCODE_PATTERNS = {
    # Structure: outward code (2 to 4 characters, starts with a letter) then inward code (digit, letter, letter).
    "GB": re.compile(r"^(GIR0AA|[A-Z]{1,2}[0-9][A-Z0-9]?[0-9][A-Z]{2})$"),
    "DE": re.compile(r"^[0-9]{5}$"),
    "FR": re.compile(r"^[0-9]{5}$"),
    "NL": re.compile(r"^[1-9][0-9]{3}[A-Z]{2}$"),
    "US": re.compile(r"^[0-9]{5}([0-9]{4})?$"),
    "ANY": re.compile(r"^[A-Z0-9][A-Z0-9]{1,8}[A-Z0-9]$"),
}

TAX_PATTERNS = {
    # GB: 9 digits, 12 digits (with branch suffix), or the GD / HA government and health forms.
    "GB": re.compile(r"^GB([0-9]{9}|[0-9]{12}|GD[0-9]{3}|HA[0-9]{3})$"),
    "DE": re.compile(r"^DE[0-9]{9}$"),
    "FR": re.compile(r"^FR[A-Z0-9]{2}[0-9]{9}$"),
    "NL": re.compile(r"^NL[0-9]{9}B[0-9]{2}$"),
    "ANY": re.compile(r"^[A-Z]{2}[A-Z0-9]{2,12}$"),
}

EMAIL_PATTERN = re.compile(r"^[^@\s,;]+@[^@\s,;]+\.[^@\s,;]{2,}$")
DEFAULT_DATE_FORMATS = ["%Y-%m-%d"]

PLACEHOLDERS = frozenset({"n/a", "na", "null", "none", "nil", "tbc", "tbd", "?", "-", "--", "unknown", "xxx"})


def is_placeholder(value: str) -> bool:
    return value.strip().lower() in PLACEHOLDERS


def valid_postcode(value: str, country: str | None) -> bool:
    ctry = normalise_country(country)
    pattern = POSTCODE_PATTERNS.get(ctry, POSTCODE_PATTERNS["ANY"])
    return bool(pattern.match(re.sub(r"[\s\-]+", "", value.upper())))


def valid_tax(value: str, country: str | None) -> bool:
    ctry = normalise_country(country)
    compact = re.sub(r"[^A-Za-z0-9]", "", value).upper()
    pattern = TAX_PATTERNS.get(ctry, TAX_PATTERNS["ANY"])
    return bool(pattern.match(compact))


def valid_email(value: str) -> bool:
    return bool(EMAIL_PATTERN.match(value.strip())) and value.strip() == value


def matching_date_format(value: str, formats: list[str]) -> str | None:
    for fmt in formats:
        try:
            datetime.strptime(value.strip(), fmt)
            return fmt
        except ValueError:
            continue
    return None


# ---------------------------------------------------------------------------
# Parts and units
# ---------------------------------------------------------------------------

DESCRIPTION_ABBREVIATIONS = {
    "s/s": "stainless steel", "ss": "stainless steel", "dia": "diameter", "blk": "black",
    "galv": "galvanised", "zp": "zinc plated", "cs": "carbon steel", "di": "ductile iron",
    "ci": "cast iron", "asm": "assembly", "assy": "assembly", "hsg": "housing",
    "brg": "bearing", "std": "standard",
}

UOM_ALIASES = {
    "EA": "EA", "EACH": "EA", "PC": "EA", "PCS": "EA", "PIECE": "EA", "NOS": "EA", "ST": "EA",
    "STK": "EA", "STUECK": "EA", "UNIT": "EA",
    "KG": "KG", "KGS": "KG", "KILO": "KG", "KILOGRAM": "KG",
    "G": "G", "GRAM": "G",
    "M": "M", "MTR": "M", "METRE": "M", "METER": "M",
    "MM": "MM", "L": "L", "LTR": "L", "LITRE": "L",
    "BOX": "BOX", "BX": "BOX", "CTN": "CTN", "CARTON": "CTN", "SET": "SET", "PAIR": "PAIR", "PR": "PAIR",
}


def normalise_uom(value: str | None, aliases: dict[str, str] | None = None) -> str:
    if not value:
        return ""
    key = fold_text(value).upper().strip().replace(".", "")
    table = UOM_ALIASES if aliases is None else {**UOM_ALIASES, **aliases}
    return table.get(key, key)


def normalise_part_number(value: str | None) -> str:
    """Upper case, drop separators, and drop leading zeros inside digit runs.

    "mc-0442-B", "MC 442 B" and "MC0442B" all become "MC442B". This can join two
    genuinely different parts, so a match is only ever a candidate for review.
    """
    if not value:
        return ""
    pn = re.sub(r"[^A-Za-z0-9]", "", value).upper()
    return re.sub(r"(?<![0-9])0+(?=[0-9])", "", pn)


def part_number_relation(a: str, b: str) -> str:
    """'equal', 'revision' (one is the other plus a short letter suffix), or 'none'."""
    if not a or not b:
        return "none"
    if a == b:
        return "equal"
    short, long_ = (a, b) if len(a) < len(b) else (b, a)
    extra = long_[len(short):]
    if long_.startswith(short) and 1 <= len(extra) <= 2 and extra.isalpha() and short[-1].isdigit():
        return "revision"
    return "none"


def normalise_description(value: str | None) -> str:
    if not value:
        return ""
    text = fold_text(value)
    for abbr, full in DESCRIPTION_ABBREVIATIONS.items():
        if "/" in abbr:
            text = re.sub(rf"(?<![a-z]){re.escape(abbr)}(?![a-z])", full, text)
    tokens = re.sub(r"[^a-z0-9]+", " ", text.replace("&", " and ")).split()
    tokens = [DESCRIPTION_ABBREVIATIONS.get(t, t) for t in tokens]
    return " ".join(" ".join(tokens).split())


# ---------------------------------------------------------------------------
# Numbers
# ---------------------------------------------------------------------------


def parse_amount(value: str, decimal_comma: bool = False) -> Decimal:
    """Parse an accounting amount. Accepts (1,234.50), 1234.50-, and leading currency signs."""
    raw = (value or "").strip()
    if raw == "":
        return Decimal("0")
    text = raw
    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative, text = True, text[1:-1]
    if text.endswith("-"):
        negative, text = True, text[:-1]
    text = text.strip().lstrip("£€$").strip()
    if text.startswith("-"):
        negative, text = (not negative), text[1:]
    text = text.replace(" ", "").replace("\u00a0", "")
    # Grouping separators must be well formed. Without this check a European amount such as
    # 1.234,56 would be read as 1.23456 by a reader expecting the other convention.
    if decimal_comma:
        grouped = r"^([0-9]{1,3}(\.[0-9]{3})+|[0-9]+)(,[0-9]+)?$"
    else:
        grouped = r"^([0-9]{1,3}(,[0-9]{3})+|[0-9]+)(\.[0-9]+)?$"
    if not re.match(grouped, text):
        raise InputError(f"'{raw}' is not a number" + (" in decimal comma format." if decimal_comma else
                                                       " in 1,234.56 format. Use --decimal-comma for 1.234,56."))
    text = text.replace(".", "").replace(",", ".") if decimal_comma else text.replace(",", "")
    try:
        amount = Decimal(text)
    except InvalidOperation as exc:
        raise InputError(f"'{raw}' is not a number.") from exc
    return -amount if negative else amount


def normalise_account_code(value: str | None) -> str:
    """Account codes are compared as text with outer spaces removed. Leading zeros are kept."""
    return (value or "").strip()
