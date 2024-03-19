# Configuration

Email-Simplified provides a way to load a handler and its config dynamically.
This is useful in applications where you want your users to be able to
configure how email is sent, rather than hard-coding a handler and config.

See [Flask-Email-Simplified] for an example of using this dynamic config.

[Flask-Email-Simplified]: https://flask-email-simplified.readthedocs.io

{func}`.get_handler_class` can be used to get a handler class by name.
Packages can register handler classes under simple names using Python's
entry point system. For example, the built-in classes are registered as
`"smtp"` and `"test"`. You can also pass a Python import path like
`"module.submodule:handler_class"`, or an already imported class.

Each handler class implements a {meth}`~.EmailHandler.from_config` class method.
This can be used to create an instance of the loaded handler from dict keys and
values rather than needing to pass keyword arguments. Handlers should document
what keys they use.

```python
from email_simplified import get_handler_class

email = get_handler_class("smtp").from_config({"port": 1025})
```
