from __future__ import annotations

import asyncio
from smtplib import SMTP
from unittest.mock import create_autospec
from unittest.mock import MagicMock
from unittest.mock import patch

from email_simplified import Message
from email_simplified import SMTPEmailHandler


def test_tls_port() -> None:
    assert SMTPEmailHandler(port=465).use_tls


def test_tls_disables_starttls() -> None:
    assert not SMTPEmailHandler(use_tls=True, use_starttls=True).use_starttls


def test_tls_context() -> None:
    assert SMTPEmailHandler(use_tls=True).tls_context
    assert SMTPEmailHandler(use_starttls=True).tls_context


def test_from_config() -> None:
    assert SMTPEmailHandler.from_config({"port": 1025, "invalid": True}).port == 1025


@patch("email_simplified.handlers.smtp.SMTP", autospec=True)
def test_connect(smtp_cls: MagicMock) -> None:
    handler = SMTPEmailHandler()
    client: MagicMock

    with handler.connect() as client:  # type: ignore[assignment]
        pass

    assert smtp_cls.call_args.kwargs.keys() == {
        "host",
        "port",
        "local_hostname",
        "timeout",
    }
    client.starttls.assert_not_called()
    client.login.assert_not_called()


@patch("email_simplified.handlers.smtp.SMTP", autospec=True)
def test_connect_setup(smtp_cls: MagicMock) -> None:
    handler = SMTPEmailHandler(use_starttls=True, username="a", password="b")
    client: MagicMock

    with handler.connect() as client:  # type: ignore[assignment]
        pass

    client.starttls.assert_called()
    client.login.assert_called()


@patch("email_simplified.handlers.smtp.SMTP_SSL", autospec=True)
def test_connect_tls(smtp_ssl_cls: MagicMock) -> None:
    handler = SMTPEmailHandler(use_tls=True)

    with handler.connect():
        pass

    assert "context" in smtp_ssl_cls.call_args.kwargs


@patch.object(SMTPEmailHandler, "connect")
def test_send(connect: MagicMock) -> None:
    ctx = create_autospec(SMTP, instance=True)
    connect.return_value.__enter__.return_value = ctx
    handler = SMTPEmailHandler()
    handler.send(
        [
            Message(subject="a"),
            Message(subject="b", from_addr="a@example.test").to_mime(),
        ]
    )
    connect.assert_called()
    assert ctx.send_message.call_count == 2


@patch.object(SMTPEmailHandler, "connect")
def test_send_empty(connect: MagicMock) -> None:
    handler = SMTPEmailHandler()
    handler.send([])
    connect.assert_not_called()


@patch.object(SMTPEmailHandler, "connect")
def test_send_batch(connect: MagicMock) -> None:
    ctx = create_autospec(SMTP, instance=True)
    connect.return_value.__enter__.return_value = ctx
    handler = SMTPEmailHandler(recipients_per_message=4)
    handler.send([Message(subject="a", to=[f"a{x}@example.test" for x in range(10)])])
    assert ctx.send_message.call_count == 3


@patch.object(SMTPEmailHandler, "connect")
def test_send_async(connect: MagicMock) -> None:
    ctx = create_autospec(SMTP, instance=True)
    connect.return_value.__enter__.return_value = ctx
    handler = SMTPEmailHandler()
    asyncio.run(handler.send_async([Message(subject="a")]))
    connect.assert_called()
    assert ctx.send_message.call_count == 1
