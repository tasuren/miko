# miko - Manager

from __future__ import annotations

from .template import Template, Any


class Manager:
    """Class for managing templates.  
    Templates rendered using this class will automatically be passed a ``manager`` variable containing an instance of this class.

    Parameters
    ----------
    *args
        Arguments to pass to :class:`miko.template.Template`.
    template_cls : Template, default Template
        This is the :class:`miko.template.Template` class used to create instances of :class:`miko.template.Template`.  
        If you extend the :class:`miko.template.Template` class and want to use the extended class with ``Manager``, use the box argument.
    extends : dict[str, Any], optional
        A dictionary of names and values of attributes to be attached to a :class:`miko.template.Template` class when it is instantiated.  
        This makes it easy to extend :class:`miko.template.Template` and access its attributes from within a template via its instance.  
        For example, if you put an instance of a web framework class as ``{\"app\": app}``, you can access ``self.app`` and its object in the template.
    **kwargs
        Keyword arguments to pass to :class:`miko.template.Template`."""

    def __init__(
        self, *args, template_cls: type[Template] = Template,
        extends: dict[str, Any] | None = None, **kwargs
    ):
        self.args, self.kwargs, self.template_cls = args, kwargs, template_cls
        self.extends = extends or {}

    def _prepare_template(self, template):
        template.manager = self
        if self.extends:
            for key, value in self.extends.items():
                setattr(template, key, value)

    def get_template(self, path: str, *args, **kwargs: dict) -> Template:
        """Prepare template from file.

        Parameters
        ----------
        path : str
            The path to the file.
        *args
            Arguments to pass to :meth:`miko.template.Template.from_file`.  
            By default, ``args`` passed when you instantiate this class is used.
        **kwargs
            Keyword arguments to pass to :meth:`miko.template.Template.from_file`.  
            By default, ``kwargs`` passed when you instantiate this class is used.

        Notes
        -----
        The class of the ``template_cls`` argument passed to :class:`miko.manager.Manager` will be used to create an instance of ``Template``."""
        template = self.template_cls.from_file(
            path, *(args or self.args), **(kwargs or self.kwargs)
        )
        self._prepare_template(template)
        return template

    async def aio_get_template(self, path: str, *args, **kwargs) -> Template:
        """This is an asynchronous version of version for :meth:`miko.manager.Manager.get_template`.

        Parameters
        ----------
        path : str
            The path to the file.
        *args
            Arguments to pass to :meth:`miko.template.Template.aio_from_file`.  
            By default, ``args`` passed when you instantiate this class is used.
        **kwargs
            Keyword arguments to pass to :meth:`miko.template.Template.aio_from_file`.  
            By default, ``kwargs`` passed when you instantiate this class is used."""
        template = await self.template_cls.aio_from_file(
            path, *(args or self.args), **(kwargs or self.kwargs)
        )
        self._prepare_template(template)
        return template

    def render(self, path: str, **kwargs) -> str:
        """Render the file from the template.

        Parameters
        ----------
        path : str
            The path to the file.
        **kwargs
            The keyword arguments to pass to :meth:`miko.template.Template.render`.

        Notes
        -----
        This method does the same thing as below.

        .. code-block:: python

            manager: Manager
            manager.get_template(path).render(**kwargs)

        Examples
        --------
        .. code-block:: html
          :caption: Template

          <title>^^ title ^^</title>

        .. code-block:: python
          :caption: Backend

          manager.render("template.html", title=title)"""
        return self.get_template(path).render(**kwargs)

    async def aiorender(self, path: str, **kwargs) -> str:
        """This is an asynchronous version of version for :meth:`miko.manager.Manager.render`.

        Parameters
        ----------
        path : str
            The path to the file.
        **kwargs
            Keyword arguments to pass to :meth:`miko.template.Template.aiorender`"""
        return await (await self.aio_get_template(path)).aiorender(**kwargs)