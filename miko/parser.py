# miko - Parser

from __future__ import annotations

from typing import Iterator


def extract_blocks(template: str) -> Iterator[tuple[int, bool, str]]:
    """Extract a block of template from a string.

    Parameters
    ----------
    template : str
        Target text

    Yields
    ------
    tuple[int, bool, str]
        This is a tuple of an integer for how many blocks, a boolean for whether it is a block, and the body."""
    now, may = "", False
    block, index = False, 0
    # ブロックを取得します。
    for character in template:
        # tempylateのブロックかどうかを調べる。
        if character == "^":
            if may:
                # ブロック終了時にはそのブロックを追加する。
                if block:
                    index += 1
                yield index, block, now[:-1]
                now, block = "", not block
                continue
            else:
                may = True
        elif may:
            may = False
        # blockを書き込んでいく。
        now += character
    yield index, block, now