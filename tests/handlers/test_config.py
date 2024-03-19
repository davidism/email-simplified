from __future__ import annotations

import pytest

from email_simplified import get_handler_class
from email_simplified import SMTPEmailHandler
from email_simplified import TestEmailHandler
from email_simplified.handlers import EmailHandler


@pytest.mark.parametrize(
    ("name", "expect"), [("smtp", SMTPEmailHandler), ("test", TestEmailHandler)]
)
def test_get_entry_point(name: str, expect: type[EmailHandler]) -> None:
    cls = get_handler_class(name)
    assert cls is expect


def test_get_import() -> None:
    cls = get_handler_class("email_simplified.handlers.smtp:SMTPEmailHandler")
    assert cls is SMTPEmailHandler


def test_get_class() -> None:
    cls = get_handler_class(SMTPEmailHandler)
    assert cls is SMTPEmailHandler


def test_get_error() -> None:
    with pytest.raises(ValueError):
        get_handler_class("nothing")


def test_from_config() -> None:
    handler = SMTPEmailHandler.from_config({"port": 1025})
    assert handler.port == 1025
