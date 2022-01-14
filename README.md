[![PyPI](https://img.shields.io/pypi/v/miko-tpl)](https://pypi.org/project/miko-tpl/) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/miko-tpl) ![PyPI - Downloads](https://img.shields.io/pypi/dm/miko-tpl) ![PyPI - License](https://img.shields.io/pypi/l/miko-tpl) [![Documentation Status](https://readthedocs.org/projects/miko/badge/?version=latest)](https://miko.readthedocs.io/en/latest/?badge=latest) [![Discord](https://img.shields.io/discord/777430548951728149?label=chat&logo=discord)](https://discord.gg/kfMwZUyGFG)
# miko
miko is a pythonic template engine that is little, lightweight and fast.

**Features:**
* Full python syntax. So there is absolutely nothing to remember in the syntax.
* It runs in Python.
* Little, lightweight and fast. (No dependency)
* Inheriting layouts through template inheritance.
* Easy to use!

## Installation
You can install it using pip.  
`$ pip install miko-tpl`

## Examples
### Title
```html
<title>^^ title ^^</title>
```
### Members
```html
<body>
  <h1>^^ team.name ^^ members</h1>
  <ul>
    ^^
      "".join(
        f'<li><a href="{ member.url }">{ member.name }</a></li>'
        for member in team.members
      )
    ^^
  </ul>
</body>
```
### Extend
```python
^^
  manager.render(
      "blog_page_layout.html", title="My sixteenth birthday.",
      content="""
        <strong>Today is my birthday!</strong><br>
        So give me a gift.
      """
  )
  # or self.extends(...)
^^
```

## Documentation
You can view the UserGuide and API reference of miko [here](https://miko.readthedocs.io/en/latest).

## Contributing
You can contribute on the development of miko in the GitHub repository.  
If you send a pull request, please keep the following in mind.  
The source code is written in such a way that it is 45% compliant with PEP8.  
I would like you to keep the overall style of the source code as unchanged as possible.

## License
miko is available under the MIT license.  
Detail: [LICENSE](https://github.com/tasuren/miko/blob/main/LICENSE)
