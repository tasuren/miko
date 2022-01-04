# tempylate - Template

from __future__ import annotations

from typing import Callable, Union, Optional, Any, DefaultDict

from importlib._bootstrap_external import _code_type
from inspect import cleandoc
import ast

from asyncio import AbstractEventLoop
from collections import defaultdict

from .utils import _executor_function
from .parser import extract_blocks
from .filters import _builtins


__all__ = (
    "TypeTempylateFunction", "caches", "BeforeFilter", "AfterFilter",
    "DEFAULT_BEFORE_FILTERS", "DEFAULT_AFTER_FILTERS", "DEFAULT_BUILTINS",
    "Block", "BlockManager", "blocker", "Template"
)
TypeTempylateFunction = Callable[..., Union[str, Any]]
"The type of a function that wraps the code of block."
_BLOCK_FUNCTION_CODE = "def __tempylate_function(<<args>>):..."
# テンプレートにあったブロックを実行するための関数
DEFAULT_BUILTINS = _builtins
"Default builtins."


class Block:
    """This class represents a block.  
    When instantiated, it compiles the string of the passed block.

    Parameters
    ----------
    text : str
        The string of the block.
    args : tuple[str, ...]
        A tuple of the names of the values that would be passed to the template.
    path : str, default ""
        The path to the template file where the block is located.  
        This is to make it easier to find the error location when an error occurs in the code in the block.  
        So, even if it doesn't make sense, it will work fine.
    index : int
        The number of how many blocks.  
        This is also just used to make it easier to find the error location when an error occurs in the code within a block."""

    def __init__(
        self, text: str, args: tuple[str, ...], *, path: str = "", index: int = 0
    ):
        self.text, self.path, self.index, self.args = text, path, index, args

        # ブロック内のコードを実行する関数を構成してバイトコンパイルする。
        code = ast.parse(_BLOCK_FUNCTION_CODE.replace("<<args>>", ",".join(self.args), 1))
        assert isinstance(code.body[-1], ast.FunctionDef)
        del code.body[-1].body[-1]
        cleaned_block = cleandoc(self.text)
        if isinstance((block_code := ast.parse(cleaned_block)).body[-1], ast.Expr):
            # `%% user.name %%`のようにテンプレートに文字列を配置できるようにするためにもし最後に`return`がなければ配置する。
            block_code.body.append(ast.Return(block_code.body.pop(-1).value)) # type: ignore
        code.body[-1].body.extend(block_code.body)
        ast.fix_missing_locations(code)
        code = compile(code, f"<{self.index}th block of {self.path} template>", "exec")
        assert isinstance(code, _code_type)
        # 関数を作る。
        namespace: dict[str, Any] = {}
        exec(code, namespace)
        self.function: TypeTempylateFunction = namespace["__tempylate_function"]

    def __str__(self) -> str:
        return f"<Block text={self.text} args={self.args} path={self.path} function={self.function}>"


class BlockManager:
    """This is a cache management class that takes a block from a template string, compiles the code for that block, and caches it.  
    It is instantiated internally and used in a variable named `blocker`.

    Attributes
    ----------
    caches : DefaultDict[str, dict[tuple[str, ...], dict[int, Block]]]"""

    caches: DefaultDict[str, dict[tuple[str, ...], dict[int, Block]]] = \
        defaultdict(lambda : defaultdict(dict))

    def get_block(
        self, path: str, args: tuple[str, ...], index: int, text: str
    ) -> Block:
        """Turn the string in the passed block into a block object.  
        It also creates a cache and returns the cache the next time the same string is passed.

        Parameters
        ----------
        path : str
            The path of the file for that template string.  
            If you give a non-file string, put the name of the content of the string, because this path is used for naming associations in cache.  
            So make sure it is unique for each template string you pass, or you will end up creating a cache every time.
        args : tuple[str, ...]
            A tuple of the names of the values that would be passed to the template.  
            This is also used to associate blocks in the cache, so it shouldn't be something that changes all the time.  
            If this method is called on the same template and this args is always changing, it will create a cache everytime.
        index : int
            The number of how many blocks are in the block.  
            This is associated in the block cache and must be unique for each block.  
            It is also used for error messages for code in the block.
        text : str
            The string of the block."""
        block, update = self.caches[path][args].get(index), False
        if block is None:
            update = True
        elif block.text != text:
            # もしブロック内のコードが変更されている場合はそのブロックがあるキャッシュを全て削除する。
            del self.caches[path]
            update = True
        if update:
            self.caches[path][args][index] = block = Block(
                text, args, path=path, index=index
            )
        assert block is not None
        return block
blocker = BlockManager()


class Template:
    """Template class.  

    Parameters
    ----------
    template : str
        Template text.
    path : str, default "unknown"
        The path to the file of template text.  
        This is not a requirement.  
        It is only used for error messages.
    builtins : dict[str, Builtin], default DEFAULT_BUILTINS
        A dictionary of names and values of variables to be passed by default when executing blocks in the template.

    Attributes
    ----------
    template : str
    path : str
    builtins : dict[str, Builtin]"""

    def __init__(
        self, template: str, *, path: str = "unknown", builtins: dict = DEFAULT_BUILTINS
    ):
        self.template, self.path = template, path
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

    def render(self, include_globals: bool = True, **kwargs) -> str:
        """Render the template.

        Parameters
        ----------
        include_globals : bool, default True
            Whether to include the data in the dictionary that can be retrieved by `globals()` in the variables passed to the code in the block.
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
        # ビルトインを混ぜる。
        kwargs.update(self.builtins)
        # ブロックの中身を実行していく。
        args = tuple(kwargs.keys())
        return "".join(
            blocker.get_block(self.path, args, index, text).function(**kwargs)
            if is_block else text
            for index, is_block, text in extract_blocks(self.template)
        )

    async def aiorender(
        self, *args, eloop: Optional[AbstractEventLoop] = None, **kwargs
    ) -> str:
        """This is an asynchronous version of `render`.  
        Use the `run_in_executor` of event loop.

        Parameters
        ----------
        *args
            Arguments to pass to `render`.
        eloop : AbstractEventLoop, optional
            The event loop to use.  
            If not specified, it will be obtained automatically.
        **kwargs
            Keyword arguments to pass to `render`."""
        return await _executor_function(self.render, eloop, *args, **kwargs)