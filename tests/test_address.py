from __future__ import annotations

from email.headerregistry import Address

import pytest

from email_simplified.address import AddressList
from email_simplified.address import prepare_address


@pytest.mark.parametrize(
    ("value", "expect"),
    [
        ("a@a.test", Address(addr_spec="a@a.test")),
        ("あ@あ.test", Address(username="あ", domain="xn--l8j.test")),
        ("A <a@a.test>", Address(display_name="A", addr_spec="a@a.test")),
        (Address(addr_spec="a@a.test"), Address(addr_spec="a@a.test")),
        (
            Address(username="あ", domain="あ.test"),
            Address(username="あ", domain="xn--l8j.test"),
        ),
    ],
)
def test_prepare_address(value: str | Address, expect: Address) -> None:
    assert prepare_address(value) == expect


def test_list_init() -> None:
    data = AddressList(["a@a.test"])
    assert data[0] == Address(addr_spec="a@a.test")


def test_list_init_empty() -> None:
    data = AddressList()
    assert not data


def test_list_append() -> None:
    data = AddressList()
    data.append("a@a.test")
    assert data[0] == Address(addr_spec="a@a.test")


def test_list_extend() -> None:
    data = AddressList()
    data.extend(["a@a.test", "b@a.test"])
    assert len(data) == 2
    assert all(isinstance(x, Address) for x in data)


def test_list_index() -> None:
    data = AddressList(["b@a.test", "a@a.test"])
    assert data.index("a@a.test") == 1


def test_list_count() -> None:
    data = AddressList(["a@a.test", "a@a.test"])
    assert data.count("a@a.test") == 2


def test_list_insert() -> None:
    data = AddressList(["a@a.test"])
    data.insert(0, "b@a.test")
    assert data == [Address(addr_spec="b@a.test"), Address(addr_spec="a@a.test")]


def test_list_remove() -> None:
    data = AddressList(["b@a.test", "a@a.test"])
    data.remove("b@a.test")
    assert data == [Address(addr_spec="a@a.test")]


def test_list_setitem() -> None:
    data = AddressList(["b@a.test", "a@a.test"])
    data[1] = "c@a.test"
    assert data[1] == Address(addr_spec="c@a.test")
    data[:] = ["d@a.test", "e@a.test"]
    assert data == [Address(addr_spec="d@a.test"), Address(addr_spec="e@a.test")]


def test_list_iadd() -> None:
    data = AddressList(["a@a.test"])
    data += ["b@a.test", "c@a.test"]
    assert len(data) == 3


def test_list_contains() -> None:
    data = AddressList(["a@a.test"])
    assert "a@a.test" in data
    assert "b@a.test" not in data
    assert object() not in data
