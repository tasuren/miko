# tempylate - Filters

from __future__ import annotations

from typing import Callable, Union, Any

from .utils import _get_all


__all__ = ("truncate",)
Builtin = Callable[..., Union[str, Any]]


def truncate(text: str, length: int = 255, end: str = "...") -> str:
    """Truncate text.

    Parameters
    ---------
    text : str
    length : int, default 255
        Max text length.
    end : str, default "..."
        The characters that come at the end of the text.

    Returns
    -------
    truncated text : str

    Examples
    --------
    ```html
    <meta property="og:title" content="%% truncate(title, 30) %%">
    ```"""
    return f"{text[:length]}{end}"


_builtins = _get_all(globals(), __all__)