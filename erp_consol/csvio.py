"""Reading CSV extracts defensively, and writing output deterministically."""

from __future__ import annotations

import codecs
import csv
import io
import json
import os
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from .errors import InputError

CANDIDATE_DELIMITERS = [",", ";", "\t", "|"]


@dataclass
class Table:
    """A CSV file held in memory. Every value is a string exactly as read."""

    path: str
    columns: list[str]
    rows: list[dict[str, str]]
    lines: list[int]  # source line number of each row, for error messages
    encoding: str
    delimiter: str
    warnings: list[str] = field(default_factory=list)

    @property
    def name(self) -> str:
        return os.path.basename(self.path)

    def find_column(self, wanted: str) -> str | None:
        """Return the real header matching `wanted`, ignoring case and outer spaces."""
        if wanted in self.columns:
            return wanted
        matches = [c for c in self.columns if c.strip().lower() == wanted.strip().lower()]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise InputError(
                f"{self.name}: column '{wanted}' is ambiguous, it matches {', '.join(matches)}."
            )
        return None

    def resolve(self, wanted: Sequence[str], hint: str = "") -> dict[str, str]:
        """Map each wanted column name to the real header, or raise listing all that are missing."""
        found: dict[str, str] = {}
        missing: list[str] = []
        for w in wanted:
            real = self.find_column(w)
            if real is None:
                missing.append(w)
            else:
                found[w] = real
        if missing:
            raise InputError(
                f"{self.name}: missing required column(s): {', '.join(repr(m) for m in missing)}. "
                f"Columns found: {', '.join(self.columns)}." + (f" {hint}" if hint else "")
            )
        return found


def _decode(raw: bytes, path: str, encoding: str) -> tuple[str, str, list[str]]:
    warnings: list[str] = []
    name = os.path.basename(path)
    if raw.startswith(b"PK\x03\x04"):
        raise InputError(
            f"{name}: this looks like a zip or Excel workbook, not a CSV file. "
            "Export the sheet as CSV and try again."
        )
    if raw.startswith(codecs.BOM_UTF16_LE) or raw.startswith(codecs.BOM_UTF16_BE):
        return raw.decode("utf-16"), "utf-16", warnings
    if b"\x00" in raw[:4096]:
        raise InputError(f"{name}: the file contains NUL bytes, so it is not a text CSV file.")
    if encoding != "auto":
        try:
            return raw.decode(encoding), encoding, warnings
        except (UnicodeDecodeError, LookupError) as exc:
            raise InputError(f"{name}: cannot decode the file as {encoding}: {exc}") from exc
    if raw.startswith(codecs.BOM_UTF8):
        return raw.decode("utf-8-sig"), "utf-8-sig", warnings
    try:
        return raw.decode("utf-8"), "utf-8", warnings
    except UnicodeDecodeError:
        pass
    try:
        text = raw.decode("cp1252")
    except UnicodeDecodeError as exc:
        raise InputError(
            f"{name}: the file is not valid UTF-8 or Windows-1252 (byte {exc.start}). "
            "Re-export it as UTF-8, or pass --encoding with the right name."
        ) from exc
    warnings.append(
        "The file is not valid UTF-8, so it was read as Windows-1252. "
        "Check that accented characters look right, or re-export as UTF-8."
    )
    return text, "cp1252", warnings


def _sniff_delimiter(text: str) -> str:
    first = ""
    for line in text.splitlines():
        if line.strip():
            first = line
            break
    best, best_n = ",", 1
    for cand in CANDIDATE_DELIMITERS:
        try:
            n = len(next(csv.reader([first], delimiter=cand)))
        except (csv.Error, StopIteration):
            continue
        if n > best_n:
            best, best_n = cand, n
    return best


def read_table(
    path: str,
    *,
    encoding: str = "auto",
    delimiter: str | None = None,
    allow_empty: bool = False,
) -> Table:
    """Read a CSV file into a Table, raising InputError with a readable message on any problem."""
    name = os.path.basename(path)
    if not os.path.exists(path):
        raise InputError(f"{path}: file not found.")
    if os.path.isdir(path):
        raise InputError(f"{path}: this is a folder, expected a CSV file.")
    try:
        with open(path, "rb") as fh:
            raw = fh.read()
    except OSError as exc:
        raise InputError(f"{path}: cannot read the file: {exc.strerror or exc}") from exc
    text, used_encoding, warnings = _decode(raw, path, encoding)
    if not text.strip():
        raise InputError(f"{name}: the file is empty. Expected a header row and data rows.")
    delim = delimiter or _sniff_delimiter(text)
    reader = csv.reader(io.StringIO(text, newline=""), delimiter=delim)
    try:
        header_row = next(reader)
    except StopIteration:
        raise InputError(f"{name}: the file is empty. Expected a header row and data rows.")
    except csv.Error as exc:
        raise InputError(f"{name}: cannot parse the header row: {exc}") from exc
    columns = [h.strip() for h in header_row]
    if any(c == "" for c in columns):
        raise InputError(f"{name}: the header row has an empty column name. Check the delimiter.")
    lowered = [c.lower() for c in columns]
    dupes = sorted({c for c in columns if lowered.count(c.lower()) > 1})
    if dupes:
        raise InputError(f"{name}: duplicate column name(s) in the header: {', '.join(dupes)}.")

    rows: list[dict[str, str]] = []
    lines: list[int] = []
    bad_width: list[int] = []
    skipped_blank = 0
    try:
        for record in reader:
            line_no = reader.line_num
            if not record or all(v.strip() == "" for v in record):
                skipped_blank += 1
                continue
            if len(record) != len(columns):
                bad_width.append(line_no)
                continue
            rows.append(dict(zip(columns, record)))
            lines.append(line_no)
    except csv.Error as exc:
        raise InputError(f"{name}: CSV parse error near line {reader.line_num}: {exc}") from exc
    if bad_width:
        shown = ", ".join(str(n) for n in bad_width[:5])
        more = f" and {len(bad_width) - 5} more" if len(bad_width) > 5 else ""
        raise InputError(
            f"{name}: {len(bad_width)} row(s) do not have {len(columns)} fields like the header "
            f"(line {shown}{more}). Check for stray delimiters or unquoted commas. "
            f"Delimiter used: {delim!r}."
        )
    if skipped_blank:
        warnings.append(f"{skipped_blank} blank row(s) were ignored.")
    if not rows and not allow_empty:
        raise InputError(f"{name}: the file has a header but no data rows.")
    return Table(path, columns, rows, lines, used_encoding, delim, warnings)


def parse_pairs(text: str | None, allowed: Iterable[str], label: str) -> dict[str, str]:
    """Parse 'key=column,key=column' option text into a dict, checking keys."""
    result: dict[str, str] = {}
    if not text:
        return result
    allowed_set = set(allowed)
    for part in text.split(","):
        part = part.strip()
        if not part:
            continue
        if "=" not in part:
            raise InputError(f"{label}: '{part}' should look like key=column.")
        key, col = (s.strip() for s in part.split("=", 1))
        if key not in allowed_set:
            raise InputError(
                f"{label}: unknown key '{key}'. Allowed keys: {', '.join(sorted(allowed_set))}."
            )
        if not col:
            raise InputError(f"{label}: key '{key}' has no column name.")
        result[key] = col
    return result


def write_csv(path: str, header: Sequence[str], rows: Iterable[Sequence[object]]) -> None:
    """Write a CSV with LF line endings so output is byte-identical on every platform."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh, lineterminator="\n")
        writer.writerow(header)
        for row in rows:
            writer.writerow(["" if v is None else v for v in row])


def write_json(path: str, data: object) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        json.dump(data, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def write_text(path: str, text: str) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as fh:
        fh.write(text if text.endswith("\n") else text + "\n")


def read_json(path: str) -> dict:
    if not os.path.exists(path):
        raise InputError(f"{path}: file not found.")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, ValueError) as exc:
        raise InputError(f"{path}: cannot read as JSON: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError(f"{path}: expected a JSON object at the top level.")
    return data
