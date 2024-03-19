from __future__ import annotations

from email.headerregistry import Address

import pytest

from email_simplified import Attachment
from email_simplified import Message


def test_init() -> None:
    m = Message(
        subject="a",
        text="a",
        from_addr="a@a.test",
        reply_to="b@a.test",
        to=["c@a.test"],
        cc=["d@a.test"],
        bcc=["e@a.test"],
        html="<p>a</p>",
    )
    assert m.subject == "a"
    assert m.text == "a"
    assert m.html == "<p>a</p>"
    assert m.from_addr == Address(addr_spec="a@a.test")
    assert m.reply_to == Address(addr_spec="b@a.test")
    assert m.to == [Address(addr_spec="c@a.test")]
    assert m.cc == [Address(addr_spec="d@a.test")]
    assert m.bcc == [Address(addr_spec="e@a.test")]


def test_init_empty() -> None:
    m = Message()
    assert m.subject is None
    assert m.text is None
    assert m.html is None
    assert m.from_addr is None
    assert m.reply_to is None
    assert m.to == []
    assert m.cc == []
    assert m.bcc == []


@pytest.mark.parametrize("attr", ["from_addr", "reply_to"])
def test_set_from(attr: str) -> None:
    m = Message()
    setattr(m, attr, "a@a.test")
    assert getattr(m, attr) == Address(addr_spec="a@a.test")
    setattr(m, attr, None)
    assert getattr(m, attr) is None


@pytest.mark.parametrize("attr", ["to", "cc", "bcc"])
def test_set_to(attr: str) -> None:
    m = Message()
    addr = Address(addr_spec="a@a.test")
    setattr(m, attr, [addr])
    assert getattr(m, attr) == [addr]
    setattr(m, attr, [])
    assert getattr(m, attr) == []


def test_mime_headers() -> None:
    m = Message.from_mime(
        Message(
            subject="a",
            text="a",
            from_addr="あ@あ.test",
            reply_to="B <b@a.test>",
            to=["c1@a.test", "c2@a.test"],
            cc=["d1@a.test", "d2@a.test"],
            bcc=["e1@a.test", "e2@a.test"],
        ).to_mime()
    )
    assert m.subject == "a"
    assert str(m.from_addr) == "あ@xn--l8j.test"
    assert str(m.reply_to) == "B <b@a.test>"
    assert len(m.to) == 2
    assert len(m.cc) == 2
    assert len(m.bcc) == 2


def test_to_mime_headers_empty() -> None:
    m = Message.from_mime(Message(text="a").to_mime())
    assert m.subject is None
    assert m.from_addr is None
    assert m.reply_to is None
    assert not m.to
    assert not m.cc
    assert not m.bcc


def test_mime_text() -> None:
    m = Message.from_mime(Message(text="a").to_mime())
    assert m.text == "a\n"
    assert m.html is None


def test_mime_html() -> None:
    m = Message.from_mime(Message(html="<p>b</p>\n<p>c</p>").to_mime())
    assert m.text == "b\nc\n"
    assert m.html == "<p>b</p>\n<p>c</p>\n"


def test_mime_text_html() -> None:
    m = Message.from_mime(Message(text="a", html="<p>b</p>").to_mime())
    assert m.text == "a\n"
    assert m.html == "<p>b</p>\n"


def test_attachments() -> None:
    m = Message.from_mime(
        Message(
            html="a",
            attachments=[Attachment(data="null", filename="a.json")],
            inline_attachments=[Attachment(data=b"null", filename="b.json")],
        ).to_mime()
    )
    assert len(m.attachments) == 1
    assert len(m.inline_attachments) == 1


def test_no_html_attachments() -> None:
    m = Message.from_mime(
        Message(
            text="a",
            attachments=[Attachment(data="a")],
            inline_attachments=[Attachment(data="b")],
        ).to_mime()
    )
    assert len(m.attachments) == 1
    assert len(m.inline_attachments) == 0
