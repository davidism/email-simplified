# Writing a Handler

The built-in SMTP handler will be appropriate for most use cases. However, you
may wish to use another SMTP library, or use an email service that has an HTTP
API. Most services with HTTP still have SMTP as well, but they may offer
additional features not possible with SMTP.

Creating a new handler involves subclassing the base handler and overriding a
few methods. If your custom handler is for a service that others may use, you
should package and publish it on PyPI.

## Implementation

Subclass {class}`.EmailHandler` and override at least
{meth}`~.EmailHandler.send`. Override `__init__` and
{meth}`~.EmailHandler.from_config` as well to allow configuration.

```python
from email.message import EmailMessage as _EmailMessage
from typing import Any
from typing import Self
from email_simplified.handlers import EmailHandler
from email_simplified import Message

class MyEmailHandler(EmailHandler):
    def __init__(self, ...) -> None:
        ...

    @classmethod
    def from_config(cls, config: dict[str, Any]) -> Self:
        ...
        return cls(...)

    def send(self, messages: list[Message | _EmailMessage]) -> None:
        ...
```

Beyond that, your class can have any additional attributes and
methods as needed. See the built-in {class}`.SMTPEmailHandler` for an example.

### Async

The default implementation of {meth}`~.EmailHandler.send_async` uses
{func}`asyncio.to_thread` to call the sync `send` method without blocking.
Override this if you're using an async library such as [aiosmtplib] or [HTTPX],
or if you're using a different event loop such as [Trio].

[aiosmtplib]: https://pypi.org/project/aiosmtplib/
[HTTPX]: https://www.python-httpx.org
[Trio]: https://trio.readthedocs.io

## Entry Point

When packaging your handler, you can specify an entry point with a simple name
for loading with {func}`.get_handler_class`. The entry point group is named
`email_simplified.handler`, and each key should correspond to a handler class.
In `pyproject.toml`:

```toml
[project.entry-points."email_simplified.handler"]
my-email = "my_email.handler:MyEmailHandler"
```

Pick a unique name, such as the name of the service. Behavior is undefined when
two packages provide the same entry point name, although it would be unlikely
for a user to install two packages for the same provider.

```python
get_handler_class("my-email")
```

If you don't provide this, users can still pass
`"my_email.handler:MyEmailHandler"`, or import it directly.
