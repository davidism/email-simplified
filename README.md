# Email-Simplified

Email-Simplified provides a much simpler interface for creating and sending
email messages compared to Python's `email` and `smtplib` modules. It also
defines an interface for using other email sending providers that offer an API
other than SMTP.

[Flask-Email-Simplified] is an extension that integrates Email-Simplified with
Flask's configuration.

[Flask-Email-Simplified]: https://flask-email-simplified.readthedocs.io

## Install

Install from [PyPI]:

```
$ pip install email-simplified
```

[pypi]: https://pypi.org/project/email-simplified/

## Example

```python
from email_simplified.handlers import SMTPEmailHandler
from email_simplified import Message

email = SMTPEmailHandler()
message = Message(subject="Hello", text="Hello, World!", to=["world@example.test"])
email.send([message])
```

## Features

- Properly sets up TLS and uses the operating system trust store by default.
- Handles international domain names. Allows Unicode in names (assuming server
  SMTPUTF8 support).
- Generates text from HTML if only HTML content is given (although you should
  still give both to get better results).
- Handles inline HTML attachments with CID generation.
- Sync and async sending.
- Can convert to and from MIME messages, and can send MIME messages in addition
  to its own message class. This allows supporting arbitrary MIME constructs if
  you need to.
- Can batch recipients for sending with servers that restrict the number of
  recipients per message.
- Provides a test handler as well to collect instead of send messages during tests.
- Can be configured by name and config dict rather than imports and arguments,
  for framework integration.
- Complete static typing.
