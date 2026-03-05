"""
requests._types
~~~~~~~~~~~~~~~

This module contains type aliases used throughout the Requests library.
These types are for internal use and type checking purposes.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping, MutableMapping
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from typing import Protocol, TypeAlias, TypeVar

    from .auth import AuthBase
    from .cookies import RequestsCookieJar
    from .models import PreparedRequest, Response
    from .structures import CaseInsensitiveDict

    _T_co = TypeVar("_T_co", covariant=True)

    class SupportsRead(Protocol[_T_co]):
        def read(self, length: int = ...) -> _T_co: ...

    class SupportsItems(Protocol):
        def items(self) -> Iterable[tuple[Any, Any]]: ...

    # Type aliases for core API concepts (ordered by request() signature)
    UriType: TypeAlias = str | bytes

    _ParamsMappingKeyType: TypeAlias = str | bytes | int | float
    _ParamsMappingValueType: TypeAlias = (
        str | bytes | int | float | Iterable[str | bytes | int | float] | None
    )
    ParamsType: TypeAlias = (
        SupportsItems
        | tuple[tuple[_ParamsMappingKeyType, _ParamsMappingValueType], ...]
        | Iterable[tuple[_ParamsMappingKeyType, _ParamsMappingValueType]]
        | str
        | bytes
        | None
    )

    DataType: TypeAlias = (
        Iterable[bytes]
        | str
        | bytes
        | SupportsRead[str | bytes]
        | list[tuple[Any, Any]]
        | tuple[tuple[Any, Any], ...]
        | Mapping[Any, Any]
        | None
    )

    HeadersType: TypeAlias = CaseInsensitiveDict[str] | Mapping[str, str | bytes]
    HeadersUpdateType: TypeAlias = Mapping[str, str | bytes | None]

    CookiesType: TypeAlias = RequestsCookieJar | Mapping[str, str]

    # Building blocks for FilesType
    _FileName: TypeAlias = str | None
    _FileContent: TypeAlias = SupportsRead[str | bytes] | str | bytes
    _FileSpecBasic: TypeAlias = tuple[_FileName, _FileContent]
    _FileSpecWithContentType: TypeAlias = tuple[_FileName, _FileContent, str]
    _FileSpecWithHeaders: TypeAlias = tuple[
        _FileName, _FileContent, str, CaseInsensitiveDict[str] | Mapping[str, str]
    ]
    _FileSpec: TypeAlias = (
        _FileContent | _FileSpecBasic | _FileSpecWithContentType | _FileSpecWithHeaders
    )
    FilesType: TypeAlias = (
        Mapping[str, _FileSpec] | Iterable[tuple[str, _FileSpec]] | None
    )

    AuthType: TypeAlias = (
        tuple[str, str] | AuthBase | Callable[[PreparedRequest], PreparedRequest] | None
    )

    TimeoutType: TypeAlias = float | tuple[float | None, float | None] | None
    ProxiesType: TypeAlias = MutableMapping[str, str]
    HooksType: TypeAlias = dict[str, list["HookType"]] | None
    VerifyType: TypeAlias = bool | str
    CertType: TypeAlias = str | tuple[str, str] | None
    JsonType: TypeAlias = (
        None | bool | int | float | str | list["JsonType"] | dict[str, "JsonType"]
    )


# These are needed at runtime for default_hooks() return type

HookType = Callable[["Response"], Any]
HooksInputType = Mapping[str, "Iterable[HookType] | HookType"]
