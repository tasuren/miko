# tempylate - Filters

from __future__ import annotations

from typing import Callable, Union, Any

from functools import lru_cache

from .utils import _get_all


__all__ = ("include", "truncate", "CS")


@lru_cache(255)
def include(path: str) -> str:
    """Embed another file.

    Parameters
    ----------
    path : str
        The path to another file."""
    with open(path, "r") as f:
        return f.read() # TODO: テンプレートエンジンが使えない状態なのでそれに対応する。


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


CS = r"^^"
"""This is just a constant with two caret signs in it.  
Use this when you want to use two caret signs side by side in a string defined in the Python code in the block."""


_builtins = _get_all(globals(), __all__)