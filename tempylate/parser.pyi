# tempylate - Parse i

from __future__ import annotations

from collections.abc import Iterator


def extract_blocks(template: str) -> Iterator[tuple[int, bool, str]]:
    """Extract a block of tempylate from a string.

    Parameters
    ----------
    template : str
        Target text

    Yields
    ------
    tuple[int, bool, str]
        This is a tuple of an integer for how many blocks, a boolean for whether it is a block, and the body."""