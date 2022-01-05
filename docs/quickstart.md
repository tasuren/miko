# Quick Start
## Template Manager
You can use the `Manager` class to prepare templates easily, and render them easily.  
So, when you use it in the backend of a web service, you should define the `Manager` class first.
```python
from miko import Manager

manager = Manager()
```

## Syntax
In miko, the part of a template enclosed in a two-lettered hat caret is a function and is executed in Python.  
This enclosed area is called a block in miko.  
The block is replaced by the value returned by the block.  
In addition, the last line of the block is automatically replaced by `return` even if you don't write `return`.  
If you don't know, it is faster to look at an example.
### Example
#### html
```html
<title>^^ title ^^</title>
<!-- The one above is equivalent to the one below.
  `<title>^^ return title ^^</title>` -->
```
#### python
```python
manager.render("template.html", title="Hi user guide!")
```
#### Result html
```html
<title>Hi user guide!</title>
```

Of course, you can also do the following:
#### html
```html
<ul>
  ^^ "".join(f"<li>{name}</li>" for name in members) ^^
</ul>
```
#### python
```python
manager.render("template.html", members=("tasuren", "yuki", "kumi"))
```

## Builtins
A built-in is a variable that can be used from the beginning in a template block.  
There are functions and so on.
* `Template` class instance: `self`
* Insert another file: `include`
  (`miko.filters.include`)
* Truncate text: `truncate`
  (`miko.filters.truncate`)
* A constant containing a two-letter cat-halet string: `CS`
  (`miko.filters.CS`)
* `Manager` class instance: `manager` (If you used the Manager class for rendering.)

miko is still waiting for a PullRequest in the GitHub repository as there are not many yet.

## Inheriting Templates
In miko, you can inherit templates by using the attribute `render` of the instance of the `Manager` class that is automatically passed to the block.  
(Or you can use the extends attribute of an instance of the Template class.)
### Examples
#### base.html
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>miko's website - ^^ title ^^</title>
</head>
<body>
  ^^ main ^^
</body>
</html>
```
#### page1.html
```html
^^
  manager.render(
      "base.html", title="miko's first page",
      main="""
        <h1>I did it!</h1>
        I made my first webpage.
      """
  )
  # or self.extends("base.html", ...)
^^
```

## About the name miko
That it is not pronounced "maiko".  
A miko (巫女 - sibyl) is a woman who serves the Japanese gods and is found in jinja (神社 - shrines).  
I named it miko to make it look like another template engine choice for jinja, Python's famous template engine.  
If you want to see what a shrine maiden looks like, search for `巫女`.  
(If you're an anime fan, you may know this.)