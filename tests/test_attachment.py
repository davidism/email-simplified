from __future__ import annotations

import pytest

from email_simplified import Attachment


@pytest.mark.parametrize(
    ("value", "expect"), [("a", "text/plain"), (b"a", "application/octet-stream")]
)
def test_default_mimetype(value: str | bytes, expect: str) -> None:
    assert Attachment(value).mimetype == expect


@pytest.mark.parametrize(
    ("value", "expect"), [("a.html", "text/html"), ("a.invalid", "text/plain")]
)
def test_guess_mimetype(value: str, expect: str) -> None:
    assert Attachment("a", filename=value).mimetype == expect


def test_given_mimetype() -> None:
    assert Attachment("a", mimetype="text/html").mimetype == "text/html"


def test_lazy_cid() -> None:
    data = Attachment("a")
    assert data._cid is None  # pyright: ignore


def test_generate_cid() -> None:
    data = Attachment("a")
    assert data.cid
    assert data._cid is not None  # pyright: ignore
    assert data.cid == data.cid


def test_set_cid() -> None:
    data = Attachment("a")
    data.cid = "test"
    assert data._cid is not None  # pyright: ignore
    assert data.cid == "test"
