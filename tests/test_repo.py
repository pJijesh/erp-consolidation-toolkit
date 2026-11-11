"""Repository hygiene: dashes, links and documentation that must match the data files."""

import os
import re

from erp_consol.csvio import read_table

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", ".pytest_cache", "output", "node_modules"}
TEXT_SUFFIXES = {".md", ".py", ".csv", ".json", ".yml", ".toml", ".txt", ".mmd", ".svg", ".gitignore", ".gitattributes", ""}
LONG_DASHES = (chr(0x2014), chr(0x2013))  # em dash and en dash, written as code points so this file stays clean


def _files(suffixes=None):
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not d.endswith(".egg-info"))
        for name in sorted(names):
            suffix = os.path.splitext(name)[1]
            if suffixes is None or suffix in suffixes:
                yield os.path.join(base, name)


def _read(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1252")  # the ERP B example files are Windows-1252 on purpose


def test_no_long_dashes_in_any_text_file():
    offenders = []
    for path in _files():
        if os.path.splitext(path)[1] in (".png",):
            continue
        text = _read(path)
        if any(d in text for d in LONG_DASHES):
            offenders.append(os.path.relpath(path, ROOT))
    assert offenders == []


def test_relative_markdown_links_resolve():
    link = re.compile(r"\]\(([^)\s]+)\)")
    broken = []
    for path in _files({".md"}):
        for target in link.findall(_read(path)):
            if re.match(r"^[a-z]+://|^#|^mailto:", target):
                continue
            target = target.split("#")[0]
            if not target:
                continue
            if not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(path), target))):
                broken.append(f"{os.path.relpath(path, ROOT)} -> {target}")
    assert broken == []


def test_every_criterion_and_gate_is_described_in_the_decision_readme():
    with open(os.path.join(ROOT, "decision", "README.md"), encoding="utf-8") as fh:
        readme = fh.read()
    table = read_table(os.path.join(ROOT, "decision", "criteria.csv"))
    ids = [row["id"] for row in table.rows]
    assert len(ids) == 17
    for ident in ids:
        assert ident in readme, f"{ident} is in criteria.csv but not in decision/README.md"


def test_rendered_diagrams_are_committed_beside_their_sources():
    images = os.path.join(ROOT, "docs", "images")
    for name in os.listdir(images):
        if name.endswith(".mmd"):
            stem = name[:-4]
            assert os.path.exists(os.path.join(images, stem + ".svg")), f"{stem}.svg missing"
            assert os.path.exists(os.path.join(images, stem + ".png")), f"{stem}.png missing"


def test_readme_has_the_expected_labels_in_order():
    with open(os.path.join(ROOT, "README.md"), encoding="utf-8") as fh:
        text = fh.read()
    positions = [text.index(label) for label in ("**Problem:**", "**For:**", "**Demonstrates:**")]
    assert positions == sorted(positions)
    for heading in ("## Quick start", "## Limitations", "## Verification status", "## Licence"):
        assert heading in text
