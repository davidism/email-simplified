from __future__ import annotations

import asyncio

from email_simplified import Message
from email_simplified import TestEmailHandler


def test_handler() -> None:
    handler = TestEmailHandler()
    handler.send([Message(subject="a")])
    asyncio.run(handler.send_async([Message(subject="b")]))
    assert len(handler.outbox) == 2


def test_config() -> None:
    TestEmailHandler.from_config({"invalid": True})
