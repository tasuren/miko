# miko - setup

from setuptools import setup
from os.path import exists


NAME = "miko"


if exists("README.md"):
    with open("README.md", "r") as f:
        long_description = f.read()
else:
    long_description = "Little, lightweight and fast template engine."


with open(f"{NAME}/__init__.py", "r") as f:
    text = f.read()
    version = text.split('__version__ = "')[1].split('"')[0]
    author = text.split('__author__ = "')[1].split('"')[0]


setup(
    name=NAME,
    version=version,
    description='Little, lightweight and fast template engine.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=f'https://github.com/tasuren/{NAME}',
    project_urls={
        "Source Code": f"https://github.com/tasuren/miko",
        "Documentation": f"https://{NAME}.readthedocs.io/"
    },
    author=author,
    author_email='tasuren@aol.com',
    license='MIT',
    keywords='template engine',
    packages=["miko"],
    install_requires=[],
    extras_requires={},
    python_requires='>=3.8.0',
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "Topic :: Text Processing :: Markup :: HTML",
        'Typing :: Typed'
    ]
)