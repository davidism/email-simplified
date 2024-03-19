from __future__ import annotations

import asyncio
import importlib.metadata
import pkgutil
import typing as t
from email.message import EmailMessage as _EmailMessage
from inspect import isclass

from ..message import Message


class EmailHandler:
    """Interface for sending email messages. Subclasses will define how to send
    using a service, such as SMTP, an email provider's API, etc.
    """

    def send(self, messages: list[Message | _EmailMessage]) -> None:
        """Send one or more email messages.

        Messages should typically be :class:`.Message`. However, they may also
        be :class:`email.message.EmailMessage` for cases where a non-standard
        MIME construction is needed. It is up to the handler to decide whether
        that is supported based on what their service is capable of.

        :param messages: A list of messages to send.
        """
        raise NotImplementedError

    async def send_async(self, messages: list[Message | _EmailMessage]) -> None:
        """Send one or more email messages, as with :meth:`send`, but in an
        ``async`` context.
        """
        await asyncio.to_thread(self.send, messages)

    @classmethod
    def from_config(cls, config: dict[str, t.Any]) -> t.Self:
        """Create an instance of this handler using arguments from ``config`` as
        needed. This is useful for frameworks when paired with
        :func:`get_handler_class`, allowing the deployment to configure an
        arbitrary handler and its arguments.
        """
        raise NotImplementedError


_handler_classes: dict[str, type[EmailHandler]] = {}


def get_handler_class(name: str | type[EmailHandler]) -> type[EmailHandler]:
    """Get a :class:`.EmailHandler` implementation by name.

    First looks up if the name is in the ``email_simplified.handler`` entry
    point namespace, and loads the referenced class if it is. Libraries
    providing handler implementations should register a handler's name so that
    it's automatically available when installed.

    If an entry point is not found, attempts to treat the name as an import
    path in the form ``module.submodule:handler_class``. This is useful for
    users writing their own handler locally where adding an entry point may not
    be possible. May also be passed an actual handler class, in which case it's
    returned directly.

    :param name: The registered entry point name, import path, or handler class
        to load and return.
    """
    if not isinstance(name, str):
        return name

    if not _handler_classes:
        for ep in importlib.metadata.entry_points(group="email_simplified.handler"):
            obj = ep.load()
            _handler_classes[ep.name] = obj

    if name in _handler_classes:
        return _handler_classes[name]

    try:
        obj = pkgutil.resolve_name(name)
    except ImportError:
        obj = None

    if isclass(obj) and issubclass(obj, EmailHandler):
        _handler_classes[name] = obj
        return obj

    raise ValueError(f"Could not find installed entry point or import: '{name}'.")
