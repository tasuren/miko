# tempylate - Filters

from inspect import cleandoc

from .utils import _get_all


__af_all__ = ("clean_text",)
__bf_all__ = ()
__all__ = __af_all__ + __bf_all__


#   After Filters
def clean_text(text: str) -> str:
    return cleandoc(text)


_afilters = _get_all(globals(), __af_all__, "only_value")
_bfilters = _get_all(globals(), __bf_all__, "only_value")