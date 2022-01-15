# miko - Builtins

from __future__ import annotations

from collections import defaultdict
from html import escape
from os import stat

from .utils import _get_all


__all__ = ("include", "escape", "truncate", "CS")


_include_caches: defaultdict[str, list] = defaultdict(lambda : [0, None])
def include(path: str) -> str:
    """Insert other files.

    Parameters
    ----------
    path : str
        The path to a file.

    Notes
    -----
    Use the last modified date of the file to cache it.

    See Also
    --------
    Template.extends : Render and embed other files."""
    mtime = stat(path).st_mtime
    if mtime == _include_caches[path][0]:
        return _include_caches[path][1]
    _include_caches[path][0] = mtime
    with open(path, "r") as f:
        _include_caches[path][1] = f.read()
    return _include_caches[path][1]


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
    .. code-block:: html

      <meta property="og:title" content="^^ truncate(title, 30) ^^">"""
    return f"{text[:length]}{end}"


CS = r"^^"
"""This is just a constant with two caret signs in it.  
Use this when you want to use two caret signs side by side in a string defined in the Python code in the block."""


_builtins = _get_all(globals(), __all__)