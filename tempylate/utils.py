# tempylate - Utils


def _get_all(globals_, all_, mode="dict"):
    if mode == "dict":
        return {
            key: value for key, value in globals_.items() if key in all_
        }
    elif mode == "only_value":
        return [
            value for key, value in globals_.items() if key in all_
        ]