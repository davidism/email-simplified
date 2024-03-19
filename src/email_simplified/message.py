from __future__ import annotations

import collections.abc as cabc
import html.parser
import typing as t
from email.headerregistry import Address
from email.headerregistry import AddressHeader
from email.message import EmailMessage as _EmailMessage

from .address import AddressList
from .address import prepare_address
from .attachment import Attachment


class Message:
    """A representation of the typical data found in an email message. Can be
    converted to and from an :class:`email.message.EmailMessage`.

    While unlikely, MIME messages can be constructed pretty much arbitrarily.
    This class only represents a "common"/"standard" message structure with
    text, HTML, download attachments, and inline attachments.

    Addresses passed to the various arguments/attributes can be strings in the
    form ``user@domain`` or ``Name <user@domain>``, or instances of
    :class:`email.headerregistry.Address`. If the ``user`` part has non-ASCII
    characters, SMTP servers must support the ``SMTPUTF8`` extension. The domain
    part will be encoded using IDNA.

    :param subject: The text in the subject line of the message.
    :param text: The plain text content.
    :param from_addr: The address to show the message was sent from.
    :param reply_to: Instruct users to reply to this address rather than
        ``from_addr``.
    :param to: The primary recipients, visible and replied to by all other
        recipients.
    :param cc: The secondary recipients, visible and replied to by all other
        recipients.
    :param bcc: Hidden recipients. Not visible or replied to by any other
        recipients. When sending mass email, use this instead of ``to`` and
        ``cc`` to avoid "reply all email storms".
    :param attachments: Downloadable files separate from the content.
    :param html: The HTML text content. ``text`` content should also be
        provided, but if it's not then text is extracted from the HTML.
    :param inline_attachments: Files that can be linked and displayed inside
        HTML content. Only relevant when ``html`` content is provided.
    """

    def __init__(
        self,
        *,
        subject: str | None = None,
        text: str | None = None,
        from_addr: str | Address | None = None,
        reply_to: str | Address | None = None,
        to: list[str | Address] | None = None,
        cc: list[str | Address] | None = None,
        bcc: list[str | Address] | None = None,
        attachments: list[Attachment] | None = None,
        html: str | None = None,
        inline_attachments: list[Attachment] | None = None,
    ):
        self.subject: str | None = subject
        """The text in the subject line of the message."""

        self.text: str | None = text
        """The plain text content."""

        self.html: str | None = html
        """The HTML text content. :attr:`text` content should also be provided,
        but if it's not then text is extracted from the HTML.
        """

        if from_addr:
            self._from_addr: Address | None = prepare_address(from_addr)
        else:
            self._from_addr = None

        if reply_to:
            self._reply_to: Address | None = prepare_address(reply_to)
        else:
            self._reply_to = None

        self._to: AddressList = AddressList(to or ())
        self._cc: AddressList = AddressList(cc or ())
        self._bcc: AddressList = AddressList(bcc or ())

        self.attachments: list[Attachment] = attachments or []
        """Downloadable files separate from the content."""

        self.inline_attachments: list[Attachment] = inline_attachments or []
        """Files that can be linked and displayed inside HTML content. Only
        relevant when :attr:`html` content is provided.
        """

    @property
    def from_addr(self) -> Address | None:
        """The address to show the message was sent from."""
        return self._from_addr

    @from_addr.setter
    def from_addr(self, value: str | Address | None) -> None:
        if value:
            self._from_addr = prepare_address(value)
        else:
            self._from_addr = None

    @property
    def reply_to(self) -> Address | None:
        """Instruct users to reply to this address rather than :attr:`from_addr`."""
        return self._reply_to

    @reply_to.setter
    def reply_to(self, value: str | Address | None) -> None:
        if value:
            self._reply_to = prepare_address(value)
        else:
            self._reply_to = None

    @property
    def to(self) -> AddressList:
        """The primary recipients, visible and replied to by all other recipients."""
        return self._to

    @to.setter
    def to(self, value: cabc.Iterable[str | Address]) -> None:
        self._to[:] = value

    @property
    def cc(self) -> AddressList:
        """The secondary recipients, visible and replied to by all other recipients."""
        return self._cc

    @cc.setter
    def cc(self, value: cabc.Iterable[str | Address]) -> None:
        self._cc[:] = value

    @property
    def bcc(self) -> AddressList:
        """Hidden recipients. Not visible or replied to by any other recipients
        When sending mass email, use this instead of :attr:`to` and :attr:`cc`
        to avoid "reply all email storms".
        """
        return self._bcc

    @bcc.setter
    def bcc(self, value: cabc.Iterable[str | Address]) -> None:
        self._bcc[:] = value

    def to_mime(self) -> _EmailMessage:
        """Convert this :class:`email_simplified.Message` to an
        :class:`email.message.EmailMessage`.
        """
        message = _EmailMessage()

        if self.subject:
            message["Subject"] = self.subject

        if self.from_addr:
            message["From"] = self.from_addr

        if self.reply_to:
            message["Reply-To"] = self.reply_to

        if self.to:
            message["To"] = self.to

        if self.cc:
            message["CC"] = self.cc

        if self.bcc:
            message["BCC"] = self.bcc

        if self.text:
            message.set_content(self.text)
        elif self.html:
            text = _HTMLToText.process(self.html)
            message.set_content(text)

        if self.html:
            message.add_alternative(self.html, subtype="html")
            part = t.cast(_EmailMessage, message.get_payload(1))

            for attachment in self.inline_attachments:
                attachment.add_to_mime(part, inline=True)

        for attachment in self.attachments:
            attachment.add_to_mime(message)

        return message

    @classmethod
    def from_mime(cls, message: _EmailMessage) -> t.Self:
        """Convert an :class:`email.message.EmailMessage` message to a
        :class:`email_simplified.Message`.

        MIME messages can potentially have arbitrary structures. This only
        supports converting from a "standard" structure where a message
        has text, html, inline attachment, and download attachment parts. Can
        be one of the following:

        -   One ``text/plain`` part.
        -   One ``multipart/alternative`` part containing one ``text/plain``
            part then either:

            -   One ``text/html`` part.
            -   One ``multipart/related`` part containing one ``text/html`` part
                then one or more inline attachment parts.

        -   One ``multipart/mixed`` part containing one of the above parts then
            one or more download attachment parts.

        :param message: The MIME part message to convert.
        """
        original = message
        content_type = original.get_content_type()
        parts: list[_EmailMessage]
        text: str
        html: str | None
        attachments: list[Attachment] = []
        inline_attachments: list[Attachment] = []

        if content_type == "multipart/mixed":
            message, *parts = t.cast(list[_EmailMessage], original.get_payload())
            content_type = message.get_content_type()

            for part in parts:
                attachments.append(
                    Attachment(
                        data=part.get_content(),
                        filename=part.get_filename(),
                        mimetype=part.get_content_type(),
                    )
                )

        if content_type == "multipart/alternative":
            text_part: _EmailMessage
            html_part: _EmailMessage
            text_part, html_part = t.cast(list[_EmailMessage], message.get_payload())
            text = text_part.get_content()

            if html_part.get_content_type() == "multipart/related":
                html_part, *parts = t.cast(list[_EmailMessage], html_part.get_payload())

                for part in parts:
                    attachment = Attachment(
                        data=part.get_content(),
                        filename=part.get_filename(),
                        mimetype=part.get_content_type(),
                    )
                    attachment.cid = part["content-id"]
                    inline_attachments.append(attachment)

            html = html_part.get_content()
        else:
            text = message.get_content()
            html = None

        from_addr: AddressHeader = original["from"]
        reply_to: AddressHeader = original["reply-to"]
        to: AddressHeader = original["to"]
        cc: AddressHeader = original["cc"]
        bcc: AddressHeader = original["bcc"]
        return cls(
            subject=original["subject"],
            text=text,
            from_addr=from_addr.addresses[0] if from_addr else None,
            reply_to=reply_to.addresses[0] if reply_to else None,
            to=list(to.addresses) if to else [],
            cc=list(cc.addresses) if cc else [],
            bcc=list(bcc.addresses) if bcc else [],
            attachments=attachments,
            html=html,
            inline_attachments=inline_attachments,
        )


class _HTMLToText(html.parser.HTMLParser):
    """Extract all text data from an HTML document. Used to create text content
    for an email if only HTML content is given.
    """

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.data: list[str] = []
        """Accumulates the text parts extracted during parsing."""

    @classmethod
    def process(cls, html: str) -> str:
        """Convert an HTML document into plain text.

        :param html: The HTML to convert.
        """
        parser = cls()
        parser.feed(html)
        return parser.text

    @property
    def text(self) -> str:
        """Join the text parts into a single string."""
        return "".join(self.data)

    def handle_data(self, data: str) -> None:
        self.data.append(data)
