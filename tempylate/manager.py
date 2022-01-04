# tempylate - Manager

from __future__ import annotations

from typing import Optional

from asyncio import AbstractEventLoop

from .utils import _executor_function
from .template import Template, Any


class BaseManager:
    """This class is the base class for `Manager` or other.  
    You can extend this class to implement more function or `render` method.  
    Parameters will be used to instantiating `Template`.

    Parameters
    ----------
    *args
    **kwargs"""

    def __init__(self, *args, **kwargs):
        self.args, self.kwargs = args, kwargs

    def get_template(self, path: str, *args, **kwargs: dict) -> Template:
        """Prepare template from file.

        Parameters
        ----------
        path : str
            The path to the file.
        **kwargs
            Keyword arguments to pass to `Template.from_file`.  
            By default, `kwargs` passed when you instantiate this class is used.

        Notes
        -----
        When instantiating `Template`, the arguments passed to `Manager` will be used to."""
        return Template.from_file(
            path, *(args or self.args), **(kwargs or self.kwargs)
        )

    def render(self, path: str, **kwargs) -> Any:
        raise NotImplementedError()

    async def aiorender(
        self, *args, loop: Optional[AbstractEventLoop] = None, **kwargs
    ) -> Any:
        raise NotImplementedError()


class Manager(BaseManager):
    """The class to maange templates.  
    Parameters are same as `BaseManager`."""

    def render(self, path: str, **kwargs) -> str:
        """Render the file from the template.

        Parameters
        ----------
        path : str
            The path to the file.
        **kwargs
            The keyword arguments to pass to `Template.render`.

        Notes
        -----
        This method does the same thing as below.
        ```python
        manager: Manager
        manager.get_template(path).render(**kwargs)
        ```

        Examples
        --------
        ```html
        <title>^^ title ^^</title>
        ```
        ```python
        manager.render("users.html", title=title, users=users)
        ```"""
        return self.get_template(path).render(**kwargs)

    async def aiorender(
        self, *args, eloop: Optional[AbstractEventLoop] = None, **kwargs
    ) -> str:
        """This is an asynchronous version of version for `render`.  
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