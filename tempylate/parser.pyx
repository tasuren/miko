# tempylate - Parser


def extract_blocks(template: str):
    now: str = ""
    cdef bint may = False
    cdef bint write = False
    # ブロックを取得します。
    for character in template:
        # tempylateのブロックかどうかを調べる。
        if character == "^":
            if may:
                if write:
                    # ブロック終了時にはそのブロックを追加する。
                    yield now[:-1]
                    write, now, before = False, "", 0
                else:
                    write = True
                continue
            else:
                may = True
        elif may:
            may = False
        # blockを書き込んでいく。
        if write:
            now += character