# miko - Template

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Union, Optional, Any, DefaultDict

from importlib._bootstrap_external import _code_type
from inspect import cleandoc
import ast

from asyncio import AbstractEventLoop
from collections import defaultdict

from .builtins import _builtins, include
from .utils import _executor_function
from .parser import extract_blocks

if TYPE_CHECKING:
    from .manager import Manager


__all__ = (
    "TypeMikoFunction", "DEFAULT_BUILTINS", "DEFAULT_ADJUSTORS",
    "Block", "CacheManager", "caches", "Template"
)
TypeMikoFunction = Callable[..., Union[str, Any]]
"The type of a function that wraps the code of block."
_BLOCK_FUNCTION_CODE = "def __miko_function(<<args>>):..."
# テンプレートにあったブロックを実行するための関数
DEFAULT_BUILTINS = _builtins
"Default builtins."
DEFAULT_ADJUSTORS = [] # type: ignore
"Default adjustors. (Empty)"
Adjustor = Callable[["Template", dict], Any]
"Type of adjustor."


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
        self, text: str, args: tuple[str, ...], template: Optional[Template] = None, *,
        path: str = "", index: int = 0
    ):
        self.text, self.path, self.index, self.args = text, path, index, args
        self.template = template

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
        self.function: TypeMikoFunction = namespace["__miko_function"]

    def __str__(self) -> str:
        return f"<Block text={self.text} args={self.args} path={self.path} function={self.function}>"


class CacheManager:
    """This is a cache management class that takes a block from a template string, compiles the code for that block, and caches it.

    Attributes
    ----------
    block_caches : DefaultDict[str, dict[tuple[str, ...], dict[int, Block]]]
    filter_caches : dict[str, Callable]"""

    block_caches: DefaultDict[str, dict[tuple[str, ...], dict[int, Block]]] = \
        defaultdict(lambda : defaultdict(dict))
    "Dictionary where the cache is stored."

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
            Number of block.
            This is associated in the block cache and must be unique for each block.  
            It is also used for error messages for code in the block.
        text : str
            The string of the block."""
        block, update = self.block_caches[path][args].get(index), False
        if block is None:
            update = True
        elif block.text != text:
            # もしブロック内のコードが変更されている場合はそのブロックがあるキャッシュを全て削除する。
            del self.block_caches[path]
            update = True
        if update:
            self.block_caches[path][args][index] = block = Block(
                text, args, path=path, index=index
            )
        assert block is not None
        return block
caches = CacheManager()


class Template:
    """Template class.  

    Parameters
    ----------
    template : str
        Template text.
    path : str, default "unknown"
        The path to the file of template text.  
        This should be unique for each template string, because it is used as the name in association with the post-compile function cache for the blocks in the template.
    builtins : dict[str, Any], default DEFAULT_BUILTINS.copy()
        A dictionary of names and values of variables to be passed by default when executing blocks in the template.
    adjustors : list[Adjustor], default DEFAULT_ADJUSTORS.copy()
        The functions in this list are called when the template is rendered.  
        When the function is called, it is passed an instance of this class (``self``) and a dictionary containing the values passed to the template.  
        This allows you to extend the value passed in.

    Attributes
    ----------
    template : str
    path : str
    builtins : dict[str, Any]
    adjustors : list[Adjustor]"""

    __original_kwargs__: dict
    __option_kwargs__: dict
    manager: Optional[Manager] = None

    def __init__(
        self, template: str, *, path: str = "unknown",
        builtins: dict[str, Any] = DEFAULT_BUILTINS.copy(),
        adjustors: list[Adjustor] = DEFAULT_ADJUSTORS.copy()
    ):
        self.template, self.path = template, path
        self.builtins, self.adjustors = builtins, adjustors

    def __new__(cls, *_, **kwargs):
        # キーワード引数を取るだけ。
        self = super().__new__(cls)
        self.__original_kwargs__ = kwargs
        self.__option_kwargs__ = kwargs.copy()
        if "path" in self.__option_kwargs__:
            del self.__option_kwargs__["path"]
        return self

    @classmethod
    def from_file(cls, path: str, *args, **kwargs) -> Template:
        """Prepare template from file easily.

        Parameters
        ----------
        path : str
            The path to the file.
        *args
            Arguments to be used when instantiating the :class:`miko.template.Template`.
        **kwargs
            Keyword arguments to be used when instantiating the :class:`miko.template.Template`."""
        return cls(include(path), path=path, *args, **kwargs)

    def render(self, include_globals: bool = True, **kwargs) -> str:
        """Render the template.

        Parameters
        ----------
        include_globals : bool, default True
            Whether to include the data in the dictionary that can be retrieved by ``globals()`` in the variables passed to the code in the block.
        **kwargs
            The name and value dictionary of the value to pass to the template.  
            Pass the value you want to use in the code in the block.

        Notes
        -----
        Each time the key of ``kwargs`` changes, the code in the block is compiled.  
        Functions created by compiling are cached.  
        Also, if you ``import`` a large library in a block, the first rendering will be slower, but after that it won't be as bad due to Python's cache.

        Warnings
        --------
        ``**kwargs`` to pass a value to the template so that the name of the value changes every time, it compiles the blocks in the template every time, which is slightly slower.  
        (I don't think anyone would do that.)  
        So you should keep the value name constant.  
        Also, if the code in the block is made to be time-consuming, rendering will take time."""
        # グローバルなものを混ぜる。
        if include_globals:
            kwargs.update(globals())
        kwargs["self"] = self
        if hasattr(self, "manager"):
            kwargs["manager"] = self.manager
        # ビルトインを混ぜる。
        kwargs.update(self.builtins)
        for decorator in self.adjustors:
            decorator(self, kwargs)
        # ブロックの中身を実行していく。
        args = tuple(kwargs.keys())
        return "".join(
            str(caches.get_block(self.path, args, index, text).function(**kwargs))
            if is_block else text
            for index, is_block, text in extract_blocks(self.template)
        )

    async def aiorender(
        self, *args, eloop: Optional[AbstractEventLoop] = None, **kwargs
    ) -> str:
        """This is an asynchronous version of :meth:`miko.template.Template.render`.  
        Use the ``run_in_executor`` of event loop.

        Parameters
        ----------
        *args
            Arguments to pass to :meth:`miko.template.Template.render`.
        eloop : AbstractEventLoop, optional
            The event loop to use.  
            If not specified, it will be obtained automatically.
        **kwargs
            Keyword arguments to pass to :meth:`miko.template.Template.render`."""
        return await _executor_function(self.render, eloop, *args, **kwargs)

    def extends(self, path: str, **kwargs) -> str:
        """Renders the file in the passed path with this class instanced by the options passed when instantiating this class.  
        It is like extends in jinja.  
        This is provided to render and embed another template within the template.  
        It seems the method of the class needs to be instantiated, which might seem cumbersome, the block is passed an instance of this class, ``self``, when the template is rendered.  
        So you can use this method in a template as follows:  
        ``^^ self.extends("template_path", keyword-arguments) ^^``

        Parameters
        ----------
        path : str
            The path to a template.
        **kwargs
            Keyword arguments to pass to :meth:`miko.template.Template.render`.

        Examples
        --------
        .. code-block:: html
            :caption: base.html

            <!DOCTYPE html>
            <html>
            <head>
                ^^ script ^^
            </head>
            <body>
                <header>My blog</header>
                <div class="title">^^ title ^^</div>
                    ^^ content ^^
                <footer>(C) 2022 tasuren</footer>
            </body>
            </html>

        .. code-block:: python
            :caption: page1.html

            ^^ self.extends(
                "base.html", script="", title="First page of my blog.",
                content=\"\"\"
                    Hi, I'm tasuren.
                \"\"\"
            ) ^^

        Notes
        -----
        Maybe the arguments of ``extends`` become too long and troublesome when you extend the web page.
        In such a case, you can create a function that calls this function internally and put it in the argument ``extends`` of the :class:`miko.manager.Manager`.
        This way it will be like an alias and more efficient.
        For example, you can do something like the following.

        .. code-block:: python
            :caption: Backend

            def blog(title, content, script=""):
                return manager.render(
                    "base.html", script=script, title=title, content=content
                )

            manager = miko.Manager(extends={"blog": blog})

        .. code-block:: python
            :caption: HTML

            ^^ self.blog(
                "My 16th birthday.", \"\"\"
                    Today I had my birthday.
                \"\"\"
            ) ^^"""
        return self.__class__.from_file(path, **self.__option_kwargs__).render(**kwargs)
