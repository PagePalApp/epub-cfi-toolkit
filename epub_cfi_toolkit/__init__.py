"""
EPUB CFI Toolkit - Python toolkit for processing EPUB CFIs.
"""

__version__ = "0.3.0"
__author__ = "PagePal"
__email__ = "info@pagepalapp.com"

from .cfi_parser import CFIParser
from .cfi_processor import CFIProcessor
from .epub_parser import EPUBParser
from .exceptions import CFIError, EPUBError

__all__ = [
    "CFIProcessor",
    "CFIParser",
    "EPUBParser",
    "CFIError",
    "EPUBError",
]
