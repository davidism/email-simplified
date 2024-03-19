# Getting Started

## Initialize the Handler

A handler implements sending email messages to an email service. The built-in
SMTP handler will be fine for most cases.

```python
from email_simplified import SMTPEmailHandler

email = SMTPEmailHandler()
```

This {class}`.SMTPEmailHandler` wraps Python's {mod}`smtplib`. It takes various
arguments to configure the client, but all arguments have default values and are
not required. By default, it connects to `localhost:25`.

See {doc}`config` for information on configuring a handler dynamically.

### Local Mail Server

The SMTP handler will fail to send if there's no server at the configured
location. During development, you can use a tool such as [mailcatcher], which
acts as a simple, local SMTP server as well as a UI for displaying any messages
it receives.

[mailcatcher]: https://github.com/sj26/mailcatcher

## Create a Message

Email-Simplified provides a {class}`.Message` class that can be used to define
the fields of a "standard" email MIME structure. It supports a text part, HTML
part, HTML inline attachments, and download attachments.

See {doc}`message` for more details.

```python
from email_simplified import Message

message = Message(
    subject="Hello",
    text="Hello, World!",
    to=["world@example.test"],
)
```

Alternatively, you may need to create a {class}`email.message.EmailMessage`
directly if you need a more complex, non-standard MIME structure.
Email-Simplified handlers can support sending both types of messages. SMTP
handlers will always convert to MIME, but other handlers for HTTP-based services
may be able to make an API call or send the MIME content directly depending on
the message structure.

## Send a Message

Call the handler's {meth}`~.EmailHandler.send` method to send the message you
created. You can pass a single message or a list of messages. Sending a list
of messages is more efficient than making multiple `send` calls, as it reuses
the same connection.

```python
email.send(message)
```

See {doc}`smtp` for more details on sending with SMTP. See {doc}`testing` for
more details on the test handler, which only stores and does not send messages
externally. See {doc}`handler` for more details on writing a handler for another
service.

### Performance

Sending messages can be a slow operation, which will delay your code from
continuing. It can be useful to send messages in background tasks, using a
system such as [RQ] or [Celery].

[RQ]: https://python-rq.org
[Celery]: https://docs.celeryq.dev

### Async

If you're calling this from an `async` function, you should `await`
{meth}`~.EmailHandler.send_async` instead.

The built-in SMTP handler uses {func}`asyncio.to_thread` to run the sync `send`
function in a thread. Other handlers can be more efficient by using an async
library such as [aiosmtplib] or [HTTPX].

[aiosmtplib]: https://pypi.org/project/aiosmtplib/
[HTTPX]: https://www.python-httpx.org
