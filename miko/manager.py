# miko - Manager

from __future__ import annotations

from typing import Type, Optional

from asyncio import AbstractEventLoop

from .utils import _executor_function
from .template import Template, Any


class Manager:
    """Class for managing templates.  
    Templates rendered using this class will automatically be passed a `manager` variable containing an instance of this class.

    Parameters
    ----------
    *args
        Arguments to pass to `Template`.
    template_cls : Template, default Template
        This is the `Template` class used to create instances of `Template`.  
        If you extend the `Template` class and want to use the extended class with `Manager`, use the box argument.
    extends : dict[str, Any], optional
        A dictionary of names and values of attributes to be attached to a `Template` class when it is instantiated.  
        This makes it easy to extend `Template` and access its attributes from within a template via its instance.
    **kwargs
        Keyword arguments to pass to `Template`."""

    def __init__(
        self, *args, template_cls: Type[Template] = Template,
        extends: Optional[dict[str, Any]] = None, **kwargs
    ):
        self.args, self.kwargs, self.template_cls = args, kwargs, template_cls
        self.extends = extends or {}
        self.extends["manager"] = self

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
        template = self.template_cls.from_file(
            path, *(args or self.args), **(kwargs or self.kwargs)
        )
        if self.extends is not None:
            for key, value in self.extends.items():
                setattr(template, key, value)
        return template

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
        .. code-block:: html
          :caption: Template

          <title>^^ title ^^</title>

        .. code-block:: python
          :caption: Backend

          manager.render("users.html", title=title)"""
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