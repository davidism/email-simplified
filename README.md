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
