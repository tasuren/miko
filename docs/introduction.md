# Introduction
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