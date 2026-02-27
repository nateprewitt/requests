"""
requests.hooks
~~~~~~~~~~~~~~

This module provides the capabilities for the Requests hooks system.

Available hooks:

``response``:
    The response generated from a Request.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Iterable, Mapping

if TYPE_CHECKING:
    from .models import Response

    _Hook = Callable[[Response], Any]
    _HooksInput = Mapping[str, Iterable[_Hook] | _Hook]

HOOKS: list[str] = ["response"]


def default_hooks() -> dict[str, list[_Hook]]:
    return {event: [] for event in HOOKS}


# TODO: response is the only one


def dispatch_hook(
    key: str,
    hooks: _HooksInput | None,
    hook_data: Response,
    **kwargs: Any,
) -> Response:
    """Dispatches a hook dictionary on a given piece of data."""
    hooks_dict = hooks or {}
    hook_list: Iterable[_Hook] | _Hook | None = hooks_dict.get(key)
    if hook_list:
        if hasattr(hook_list, "__call__"):
            hook_list = [hook_list]  # type: ignore[list-item]
        for hook in hook_list:  # type: ignore[union-attr]
            _hook_data = hook(hook_data, **kwargs)
            if _hook_data is not None:
                hook_data = _hook_data
    return hook_data
