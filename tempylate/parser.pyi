# tempylate - Parse i

from __future__ import annotations

from collections.abc import Iterator


def extract_blocks(template: str) -> Iterator[str]:
    """Extract a block of tempylate from a string.

    Parameters
    ----------
    template : str
        Target text

    Yields
    ------
    str
        Extracted block"""