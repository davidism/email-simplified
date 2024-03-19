from __future__ import annotations

import email.utils
import mimetypes
import socket
import typing as t
from email.message import EmailMessage


class Attachment:
    """Structured representation of an email attachment.

    :param data: Text or bytes data to attach.
    :param filename: Filename to show for the attachment.
    :param mimetype: Mimetype describing the attached data. Defaults to guessing
        from ``filename`` if possible, or ``text/plain`` for text data or
        ``application/octet-stream`` for bytes data.
    """

    def __init__(
        self,
        data: str | bytes,
        *,
        filename: str | None = None,
        mimetype: str | None = None,
    ):
        if mimetype is None and filename is not None:
            guess = mimetypes.guess_type(filename)[0]

            if guess is not None:
                mimetype = guess

        if mimetype is None:
            if isinstance(data, str):
                mimetype = "text/plain"
            else:
                mimetype = "application/octet-stream"

        self.data = data
        """Text or bytes data to attach."""

        self.filename = filename
        """Filename to show for the attachment."""

        self.mimetype: str = mimetype
        """Mimetype describing the attached data. Defaults to guessing from
        ``filename`` if possible, or ``text/plain`` for text data or
        ``application/octet-stream`` for bytes data.
        """

        self._cid: str | None = None

    @property
    def cid(self) -> str:
        """The id used to refer to the inline attachment in HTML. Generated on
        access if not set.
        """
        if self._cid is None:
            self._cid = email.utils.make_msgid(domain=local_hostname())

        return self._cid

    @cid.setter
    def cid(self, value: str | None) -> None:
        self._cid = value

    def add_to_mime(self, message: EmailMessage, *, inline: bool = False) -> None:
        """Add this attachment to the given :class:`email.message.EmailMessage.
        When attaching inline, include the :attr:`cid`, otherwise the
        :attr:`filename`.

        :param message: The message to attach to.
        :param inline: Attach inline for linking from HTML.
        """
        kwargs: dict[str, t.Any] = {}
        main_type, _, kwargs["subtype"] = self.mimetype.partition("/")
        data: str | bytes = self.data

        if isinstance(data, str):
            if main_type != "text":
                # For example application/json from a .json filename.
                # message.add_attachment insists on text/* mimetypes for str
                # data, so encode it as utf8 to get around that.
                data = data.encode()
                kwargs["maintype"] = main_type
        else:
            kwargs["maintype"] = main_type

        if inline:
            kwargs["cid"] = self.cid
            message.add_related(data, **kwargs)
        else:
            if self.filename:
                kwargs["filename"] = self.filename

            message.add_attachment(data, **kwargs)


_local_hostname: str | None = None
"""Cached value for :func:`local_hostname`."""


def local_hostname() -> str:
    """Return the result of :func:`socket.getfqdn`, caching the value for
    subsequent calls. Used to generate attachment cids and with SMTP.
    """
    global _local_hostname

    if _local_hostname is None:
        _local_hostname = socket.getfqdn()

    return _local_hostname
