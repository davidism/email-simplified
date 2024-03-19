# Testing

During testing, you probably don't want to actually send messages. Instead, you
can use the built-in {class}`.TestEmailHandler`, which stores all messages in a
list called {attr}`~.TestEmailHandler.outbox`. After sending messages, you can
check that the length or content of the outbox is what you expect.

```python
from email_simplified import Message
from email_simplified import TestEmailHandler

test_email = TestEmailHandler()
test_email.send(Message(...))
assert len(test_email.outbox) == 1
```
