from __future__ import annotations

import typing as t
from email.message import EmailMessage as _EmailMessage

from ..message import Message
from .base import EmailHandler


class TestEmailHandler(EmailHandler):
    """Email handler that appends messages to a list rather than sending them.
    Useful when testing.
    """

    __test__ = False  # don't get collected by pytest

    def __init__(self) -> None:
        self.outbox: list[Message | _EmailMessage] = []
        """List of messages that have been sent with this handler."""

    @classmethod
    def from_config(cls, config: dict[str, t.Any]) -> t.Self:
        return cls()

    def send(self, messages: list[Message | _EmailMessage]) -> None:
        self.outbox.extend(messages)

    async def send_async(self, messages: list[Message | _EmailMessage]) -> None:
        self.send(messages)
