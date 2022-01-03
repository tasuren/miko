# tempylate - Template

from __future__ import annotations

from typing import Callable, Union, Optional, Any

from importlib._bootstrap_external import _code_type
from inspect import cleandoc
import ast

from secrets import token_hex

from .filters import _afilters, _bfilters
from .builtins import Builtin, _builtins
from .parser import extract_blocks


# The type of a function that wraps the code of block.
TypeTempylateFunction = Callable[..., Union[str, Any]]
# からからからのからデータ
_NULL: tuple[str, dict] = (f"__NULL_{token_hex(4)}_DATA__", {})
# テンプレートにあったブロックを実行するための関数
_BLOCK_FUNCTION_CODE = "def __tempylate_function(<<args>>):..."
# 読み込んだテンプレートのブロックのコードのキャッシュ
caches: dict[
    tuple[str, int], tuple[str, dict[tuple[str, ...], TypeTempylateFunction]]
] = {}
# Filterの型
BeforeFilter = Callable[[dict], dict]
AfterFilter = Callable[[str], str]
# デフォルトのフィルター
DEFAULT_BEFORE_FILTERS: list[BeforeFilter] = _bfilters
DEFAULT_AFTER_FILTERS: list[AfterFilter] = _afilters
# デフォルトのビルトイン
DEFAULT_BUILTINS = _builtins


class Template:
    def __init__(
        self, template: str, *, path: str = "unknown", cache: bool = True,
        before_filters: list[BeforeFilter] = DEFAULT_BEFORE_FILTERS,
        after_filters: list[AfterFilter] = DEFAULT_AFTER_FILTERS,
        builtins: dict[str, Builtin] = DEFAULT_BUILTINS
    ):
        self.template, self.path, self.cache = template, path, cache
        self.before_filters, self.after_filters = before_filters, after_filters
        self.builtins = builtins
        self.rendered: Optional[str] = None

    @classmethod
    def from_file(cls, path: str, *args, **kwargs) -> Template:
        """Prepare template from file easily.

        Parameters
        ----------
        path : str
            The path to the file.
        *args
            Arguments to be used when instantiating the `Template`.
        **kwargs
            Keyword arguments to be used when instantiating the `Template`."""
        with open(path, "r") as f:
            return cls(f.read(), path=path, *args, **kwargs)

    def compile_block(
        self, block: str, args: tuple[str, ...], index: int = 0
    ) -> TypeTempylateFunction:
        """Compile code of block.

        Parameters
        ----------
        block : str
            The block in the template.
        args : Iterable[str]
            Iterable containing the names of variables that will be passed in the block.
        index : int
            Index number of the block used for the exception message.

        Returns
        -------
        TypeTempylateFunction

        Notes
        -----
        If found the a cache, it will return a cache.  
        (Cache include to `tempylate.caches`.)"""
        already = False
        if (cache := caches.get((self.path, index), _NULL))[0] == block:
            already = True
            if cache := cache[1].get(args): # type: ignore
                # 既にキャッシュがあるならそれを返す。
                return cache
        # もしキャッシュに存在しないしないブロックの場合はブロックのコードオブジェクトを作る。
        code = ast.parse(_BLOCK_FUNCTION_CODE.replace("<<args>>", ",".join(args), 1))
        assert isinstance(code.body[-1], ast.FunctionDef)
        del code.body[-1].body[-1]
        cleaned_block = cleandoc(block)
        if isinstance((block_code := ast.parse(cleaned_block)).body[-1], ast.Expr):
            # `%% user.name %%`のようにテンプレートに文字列を配置できるようにするためにもし最後に`return`がなければ配置する。
            block_code.body.append(ast.Return(block_code.body.pop(-1).value)) # type: ignore
        code.body[-1].body.extend(block_code.body)
        ast.fix_missing_locations(code)
        code = compile(code, f"<{index}th block of {self.path} template>", "exec")
        assert isinstance(code, _code_type)
        # 関数を作る。
        namespace: dict[str, Any] = {}
        exec(code, namespace)
        function = namespace["__tempylate_function"]
        if self.cache:
            # キャッシュを保存しておく。
            if already:
                caches[(self.path, index)][1][args] = function
            else:
                caches[(self.path, index)] = (block, {args: function})
        return function

    def render(
        self, include_globals: bool = True, options: dict[str, dict] = {}, **kwargs
    ) -> str:
        """Render the template.

        Parameters
        ----------
        include_globals : bool, default True
            Whether to include the data in the dictionary that can be retrieved by `globals()` in the variables passed to the code in the block.
        option : 
        **kwargs
            This is a dictionary of variable names and values that can be used in the Python code of a block of templates.

        Notes
        -----
        Each time the key of `kwargs` changes, the code in the block is compiled. (And it will be cached if `cache` attribute is not set to `False`.)  
        (Details in `compile_block`'s document.)  
        If you `import` a large library in a block, the first rendering will be slower, but after that it won't be as bad due to Python's cache.

        Warnings
        --------
        As you can think of from Notes if you pass a value like `**kwargs` and the `key` changes every time, it will slow the program down because what is it in the Notes. (But I think you don't do this.)  
        Also, if you use this template engine in a web framework and put time-consuming code in a block, it will not be able to respond."""
        # グローバルなものを混ぜる。
        if include_globals:
            kwargs.update(globals())
        # Bフィルターを実行する。
        for bfilter in self.before_filters:
            kwargs = bfilter(kwargs)
        kwargs["template"] = self.template
        # ブロックの中身を実行していく。
        for index, block in enumerate(extract_blocks(self.template)):
            text = self.compile_block(block, tuple(kwargs.keys()), index)(**kwargs)
            for afilter in self.after_filters:
                text = afilter(text)
            kwargs["template"] = kwargs["template"].replace(
                "".join((r"^^", block, r"^^")),
                text if isinstance(text, str) else str(text),
                1
            )
        return kwargs["template"]