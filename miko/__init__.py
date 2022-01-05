""".. include:: ../README.md"""
# miko by tasuren

from .template import (
    DEFAULT_BUILTINS, DEFAULT_ADJUSTORS, Adjustor,
    Template, Block, CacheManager, caches
)
from .manager import Manager
from . import filters


__version__ = "1.0.0"
__author__ = "tasuren"