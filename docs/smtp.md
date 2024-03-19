# SMTP Handler

The built-in SMTP handler wraps Python's {mod}`smtplib` with a much simpler
interface. It handles setting up and using the client, which contains some
steps that are easy to forget or get wrong when using `smtplib` manually.

Many email services offer HTTP APIs to send messages. However, even if they
don't emphasize it, they probably still offer SMTP as well. For most use cases,
SMTP will be fine. If you need specific service behavior, you can write and
publish a handler as described in {doc}`handler`.

## Configuration

All arguments to {class}`.SMTPEmailHandler` are optional. They are passed on
to {class}`smtplib.SMTP`, which has defaults for all values. In particular, the
default host and port is `localhost:25`. When using port 465, TLS is
automatically configured and operating system trust is used by default.

## TLS

If you pass `port=465`, this will automatically enable
{attr}`~.SMTPEmailHandler.use_tls`. You can also pass `use_tls=True` if the
service you use requires a different port.

When `use_tls` or `use_starttls` are enabled, a TLS context is required, which
defines what server certificates to trust. You should _never_ disable this, as
it makes TLS essentially insecure. If you don't pass a context,
{func}`ssl.create_default_context` returns a context that uses your operating
system's trust store, which is appropriate for publicly-accessible services. If
you're using custom certificates, you can use the same function and pass the
appropriate public, private, and CA certificates.

If both params are passed, `use_tls` takes precedence over `use_starttls`.
STARTTLS is often confused with true TLS, and should generally be avoided as
it is an older and less secure option. TLS will secure the entire connection,
STARTTLS will only secure the connection after an initial unsecure portion.
Make sure you find your provider's TLS port, and not their STARTTLS port. You
may also see TLS referred to as its earlier predecessor SSL.

## Gmail and OAuth

Gmail and some other providers require stricter authentication than your
username and password. This is so that you don't accidentally reveal your
full Google account credentials. Many email readers now support OAuth
authentication flows, but this is difficult to implement in applications that
don't provide direct user auth. For example, a web application needs to start
up without an admin present to go through the OAuth flow.

Look for a feature in your provider called something like "app passwords". This
generates a password that only works in limited scopes, and cannot be used to
log into your entire account. For Gmail, you can find that here
<https://support.google.com/mail/answer/185833> and here
<https://myaccount.google.com/apppasswords>.

It is possible to use OAuth rather than an app password, but how to do so is
outside the scope of these docs. In general, you'd need to start a temporary
local server to receive the authentication callback, then send the user to the
service's authentication page with the correct settings. Storing the returned
token for some time is also a good idea to avoid having to go through the auth
flow every time.

## Don't Send With a Personal Account

Using your regular mail account can seem convenient, but is probably not a good
idea. It ties your application to your identity, and often times personal mail
accounts have limits that make using them for applications difficult. Sending
"transactional" emails, such as notifications and password resets, through a
personal account can also cause the service to start considering it a source of
spam.

In development, consider using a local SMTP application such as [mailcatcher],
which can also display the emails and never sends them externally. In
production, choose a service that is designed for applications and sending large
numbers of transactional emails. Most services offer a free tier that will be
more than enough for most hobby applications.

[mailcatcher]: https://github.com/sj26/mailcatcher

## Batching Recipients

Some SMTP servers enforce a limit on the number of recipients for a single
message. We've observed this especially with Microsoft Exchange servers.

Pass `recipients_per_message=N`, where N <= the server's limit, and the handler
will automatically batch the recipients into multiple low level send calls.

At the low level, this limit seems to be the number of `RCPT` commands before a
`DATA` command. This is relevant when one message has many recipients, but is not
the same as sending many messages each with different recipients. If your server
limits the number of messages (`DATA` commands) in a single connection, you'll
need to implement batching the calls to {meth}`.SMTPEmailHandler.send` instead.
