"""
EPUB CFI Toolkit - A Python toolkit for processing EPUB Canonical Fragment Identifiers.
"""

__version__ = "0.1.0"
__author__ = "PagePal"
__email__ = "info@pagepalapp.com"

from .cfi_processor import CFIProcessor
from .cfi_validator import CFIValidator
from .cfi_parser import CFIParser
from .epub_parser import EPUBParser
from .exceptions import CFIError, CFIValidationError, EPUBError

__all__ = [
    "CFIProcessor",
    "CFIValidator",
    "CFIParser",
    "EPUBParser",
    "CFIError",
    "CFIValidationError",
    "EPUBError",
]