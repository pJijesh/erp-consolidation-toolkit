import io
import os
import sys
from contextlib import redirect_stderr, redirect_stdout

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from erp_consol.cli import main  # noqa: E402


@pytest.fixture
def root():
    return ROOT


@pytest.fixture
def write(tmp_path):
    """Write a text or bytes file under tmp_path and return its path."""

    def _write(name, content, encoding="utf-8"):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding=encoding, newline="")
        return str(path)

    return _write


@pytest.fixture
def cli():
    """Run the command line in process and return (exit status, stdout, stderr)."""

    def _cli(*argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = main([str(a) for a in argv])
            except SystemExit as exc:  # argparse exits on usage errors
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    return _cli
