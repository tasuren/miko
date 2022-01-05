# miko - Utils

from asyncio import get_event_loop, new_event_loop


def _get_all(globals_, all_, mode="dict"):
    if mode == "dict":
        return {
            key: value for key, value in globals_.items() if key in all_
        }
    elif mode == "only_value":
        return [
            value for key, value in globals_.items() if key in all_
        ]


async def _executor_function(function, loop, *args, **kwargs):
    # 渡された関数を非同期に実行します。
    close = False
    if loop is None:
        try:
            loop = get_event_loop()
        except RuntimeError:
            loop = new_event_loop()
            close = True
    result = await loop.run_in_executor(
        None, lambda : function(*args, **kwargs)
    )
    if close:
        loop.close()
    return result