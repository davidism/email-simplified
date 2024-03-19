from __future__ import annotations

import collections.abc as cabc
import email.utils
import sys
import typing as t
from email.headerregistry import Address


class AddressList(list[Address]):
    """A :class:`list` subclass that contains class:`email.headerregistry.Address`
    items, but accepts strings as well for various operations. Domains are IDNA
    encoded if needed.
    """

    def __init__(self, value: cabc.Iterable[str | Address] = (), /) -> None:
        super().__init__(prepare_address(v) for v in value)

    def append(self, value: str | Address, /) -> None:
        super().append(prepare_address(value))

    def extend(self, value: cabc.Iterable[str | Address], /) -> None:
        super().extend(prepare_address(v) for v in value)

    def index(
        self,
        value: str | Address,
        start: t.SupportsIndex = 0,
        stop: t.SupportsIndex = sys.maxsize,
        /,
    ) -> int:
        return super().index(prepare_address(value))

    def count(self, value: str | Address, /) -> int:
        return super().count(prepare_address(value))

    def insert(self, index: t.SupportsIndex, value: str | Address, /) -> None:
        super().insert(index, prepare_address(value))

    def remove(self, value: str | Address, /) -> None:
        super().remove(prepare_address(value))

    @t.overload
    def __setitem__(self, key: t.SupportsIndex, value: str | Address) -> None: ...

    @t.overload
    def __setitem__(self, key: slice, value: cabc.Iterable[str | Address]) -> None: ...

    def __setitem__(
        self,
        key: t.SupportsIndex | slice,
        value: str | Address | cabc.Iterable[str | Address],
    ) -> None:
        if not isinstance(key, slice):
            super().__setitem__(key, prepare_address(value))  # type: ignore[arg-type]
        else:
            super().__setitem__(key, (prepare_address(v) for v in value))  # type: ignore[union-attr]

    def __iadd__(self, other: cabc.Iterable[str | Address]) -> t.Self:  # type: ignore[override, misc]
        return super().__iadd__(prepare_address(v) for v in other)

    def __contains__(self, value: object) -> bool:
        if not isinstance(value, str | Address):
            return False

        return super().__contains__(prepare_address(value))


def prepare_address(address: str | Address) -> Address:
    """Convert a string or :class:`email.headerregistry.Address` to an
    ``Address`` with the domain part IDNA encoded if needed.

    :param address: Address to process.
    """
    if isinstance(address, Address):
        domain = _idna_if_needed(address.domain)

        if domain == address.domain:
            return address

        return Address(address.display_name, address.username, domain)

    name, addr = email.utils.parseaddr(address)
    username, _, domain = addr.rpartition("@")
    domain = _idna_if_needed(domain)
    return Address(name, username, domain)


def _idna_if_needed(domain: str) -> str:
    """If the domain is non-ASCII, IDNA encode it.

    :param domain: The domain to encode.
    """
    try:
        domain.encode("ascii")
    except UnicodeEncodeError:
        return domain.encode("idna").decode("ascii")

    return domain
