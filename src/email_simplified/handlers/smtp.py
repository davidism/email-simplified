from __future__ import annotations

import ssl
import typing as t
from contextlib import contextmanager
from email.message import EmailMessage as _EmailMessage
from itertools import islice
from smtplib import SMTP
from smtplib import SMTP_SSL
from smtplib import SMTP_SSL_PORT
from ssl import SSLContext

from ..attachment import local_hostname
from ..message import Message
from .base import EmailHandler


class SMTPEmailHandler(EmailHandler):
    """Email handler that sends with SMTP using Python's built-in
    :mod:`smtplib`. All arguments are optional, :class:`smtplib.SMTP` uses
    default values if something is not given.

    :param host: Host to connect to.
    :param port: Port to connect to.
    :param use_tls: The connection should be established with TLS. Default is
        ``True`` if ``port`` is 465.
    :param use_starttls: The connection should be upgraded to TLS after
        establishing a plain connection first. You should prefer ``use_tls``
        instead if your SMTP server supports it.
    :param tls_context: An :class:`ssl.SSLContext` to use when ``use_tls`` or
        ``use_starttls`` is enabled. Defaults to :func:`ssl.create_default_context`,
        which enables verifying any server cert trusted by the OS. You should
        only need to change this if the server uses a custom cert, or needs a
        client cert sent as well.
    :param timeout: Connection timeout. Default is no timeout.
    :param username: Username to log in with.
    :param password: Password to log in with.
    :param default_from: Default address to send from if the ``Sender`` or
        ``From`` header is not set on a message.
    :param recipients_per_message: If a message has more than this number of
        recipients, split the send calls to batches of this size. This is to
        support servers that have a limit configured. By default, no batching
        is done.
    """

    def __init__(
        self,
        *,
        host: str | None = None,
        port: int | None = None,
        use_tls: bool | None = None,
        use_starttls: bool = False,
        tls_context: SSLContext | None = None,
        timeout: float | None = None,
        username: str | None = None,
        password: str | None = None,
        default_from: str | None = None,
        recipients_per_message: int | None = None,
    ):
        self.host = host
        """Host to connect to."""

        self.port = port
        """Port to connect to."""

        self.timeout = timeout
        """Connection timeout."""

        self.username = username
        """Username to log in with."""

        self.password = password
        """Password to log in with."""

        self.default_from = default_from
        """Default address to send from if the ``Sender`` or ``From`` header is
        not set on a message.
        """

        self.recipients_per_message = recipients_per_message
        """If a message has more than this number of recipients, split the
        low-level send calls to batches of this size. This is to support servers
        that have a limit configured. By default no batching is done.
        """

        if use_tls is None:
            use_tls = port == SMTP_SSL_PORT

        self.use_tls = use_tls
        """The connection should be established with TLS."""

        self.use_starttls: bool = not use_tls and use_starttls
        """The connection should be upgraded to TLS after establishing a plain
        connection first.
        """

        if use_tls or use_starttls and tls_context is None:
            tls_context = ssl.create_default_context()

        self.tls_context = tls_context
        """An :class:`ssl.SSLContext` to use when ``use_tls`` or
        ``use_starttls`` is enabled.
        """

    @classmethod
    def from_config(cls, config: dict[str, t.Any]) -> t.Self:
        """Create a handler from a config dict. Config keys match the
        arguments to :class:`.SMTPEmailHandler`, and are all optional.
        """
        return cls(
            host=config.get("host"),
            port=config.get("port"),
            use_tls=config.get("use_tls"),
            use_starttls=config.get("use_starttls", False),
            tls_context=config.get("tls_context"),
            timeout=config.get("timeout"),
            username=config.get("username"),
            password=config.get("password"),
            default_from=config.get("default_from"),
        )

    @contextmanager
    def connect(self) -> t.Iterator[SMTP]:
        """Context manager that creates an :class:`smtplib.SMTP` client, connects,
        logs in, then closes when exiting the block.
        """
        smtp_cls: type[SMTP | SMTP_SSL] = SMTP
        smtp_args: dict[str, t.Any] = {
            "host": self.host,
            "port": self.port,
            "local_hostname": local_hostname(),
            "timeout": self.timeout,
        }

        if self.use_tls:
            smtp_cls = SMTP_SSL
            smtp_args["context"] = self.tls_context

        with smtp_cls(**smtp_args) as client:
            if self.use_starttls:
                client.starttls(context=self.tls_context)

            if self.username is not None and self.password is not None:
                client.login(self.username, self.password)

            yield client

    def _send_batched(
        self, client: SMTP, message: _EmailMessage, from_addr: str | None
    ) -> None:
        assert self.recipients_per_message is not None
        recipient_fields = (message["to"], message["cc"], message["bcc"])
        recipients = (
            a.addr_spec for f in recipient_fields if f is not None for a in f.addresses
        )

        # itertools.batched for Python < 3.12
        while batch := tuple(islice(recipients, self.recipients_per_message)):
            client.send_message(message, from_addr=from_addr, to_addrs=batch)

    def send(self, messages: list[Message | _EmailMessage]) -> None:
        if not messages:
            return

        with self.connect() as client:
            for message in messages:
                if isinstance(message, Message):
                    mime_message = message.to_mime()
                else:
                    mime_message = message

                from_addr = mime_message["sender"] or mime_message["from"]

                if from_addr:
                    from_addr = from_addr.addresses[0].addr_spec
                else:
                    from_addr = self.default_from

                if self.recipients_per_message:
                    self._send_batched(client, mime_message, from_addr)
                else:
                    client.send_message(mime_message, from_addr=from_addr)
