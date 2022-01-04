# tempylate - Parser


def extract_blocks(template: str):
    now: str = ""
    cdef bint may = False
    cdef bint write = False
    cdef bint block = False
    cdef int index = 0
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