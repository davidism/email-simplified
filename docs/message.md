# Creating Messages

The {class}`.Message` class provides an interface for creating "standard" email
messages. This includes text, HTML, download attachments, and inline
attachments. This wraps Python's {mod}`email.message.EmailMessage` in a much
simpler interface.

## Attachments

Attachments are represented with the {class}`.Attachment` class. Pass a list of
these attachment instances to the `attachments` parameter when creating a
message, or append to the {attr}`.Message.attachments` list later.

Email-Simplified also refers to these as "download attachments", in contrast to
"inline attachments" described below. Download attachments are typically shown
next to the message subject and can be saved and opened by the user.

## HTML and Text

A message the contains HTML content should also contain text content. This
ensures support for clients that don't support HTML or prefer viewing plain
text.

If you only set {attr}`~.Message.html` and not {attr}`~.Message.text`, then
Email-Simplified will extract the text content from the HTML. This may fail if
the HTML is invalid. Depending on the complexity of the HTML, this could look
pretty bad. It's better to pass `text` content yourself.

## HTML Inline Attachments

When specifying an HTML body for the message, you can also specify inline
attachments. These can be referenced by a special URL in the HTML, such as
in `<img src="...">` tags.

Pass a list of these attachment instances to the `inline_attachments` parameter
when creating a message, or append to the {attr}`.Message.inline_attachments`
list later.

Your message must contain an {attr}`~.Message.html` body, otherwise inline
attachments will be omitted.

To reference inline attachments in HTML, you need the attachment's CID. This
will be automatically generated when accessing {attr}`.Attachment.cid`, or can
be assigned to a custom value.

```python
from email_simplified import Attachment, Message

with open("logo.png", "rb") as f:
    image = Attachment(f.read(), filename="logo.png")

message = Message(
    text="Hello, World!",
    html=f"""\
    <p>Hello, World!</p><br>
    <img src="cid:{image.cid}">
    """,
    inline_attachments=[image],
)
```

:::{warning}
The f-string in the example above is only for demonstration purposes and can
result in unsafe HTML. If you render any user input into the HTML, you must use
a library such as [MarkupSafe] to escape the values. Or use a template library
such as [Jinja] which handles escaping.
:::

[MarkupSafe]: https://markupsafe.palletsprojects.com
[Jinja]: https://jinja.palletsprojects.com

## Addresses

Email-Simplified handles various complexities in email addresses. Addresses can
be `user@domain` or `Name <user@domain>`. If the domain part contains Unicode,
it will be IDNA encoded. If the name or user part contains Unicode, it will not
be encoded, and the server must support the SMTPUTF8 extension. There are some
rules about what addresses are valid.

Addresses are stored as Python {class}`email.headerregistry.Address` objects.
Strings can be passed to the various parameters and lists, and will be
converted. `Address` objects can be passed as well, and will IDNA be encoded if
needed. This handles keeping all values normalized and valid ahead of time.

## MIME

While unlikely, email MIME messages can be constructed pretty much arbitrarily.
The {class}`.Message` class only represents a "common"/"standard" message
structure with text, HTML, inline attachments, and download attachments.

Esoteric MIME constructs beyond that are still supported by
{meth}`.EmailHandler.send`, but must be constructed separately with Python's
{mod}`email.message`.

If you have a MIME {class}`email.message.EmailMessage` from somewhere else, you
can call Email-Simplified's {meth}`.Message.from_mime` to convert it for easier
modification in your own code. Call {meth}`.Message.to_mime` if you need to
pass it back to code that works with MIME. Both of these only support the
"standard" message structure:
