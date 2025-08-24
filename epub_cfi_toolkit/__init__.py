"""
EPUB CFI Toolkit - A Python toolkit for processing EPUB Canonical Fragment Identifiers.
"""

__version__ = "0.1.0"
__author__ = "PagePalApp"
__email__ = "contact@pagepal.app"

from .cfi_processor import CFIProcessor
from .cfi_validator import CFIValidator
from .exceptions import CFIError, CFIValidationError, EPUBError

__all__ = [
    "CFIProcessor",
    "CFIValidator",
    "CFIError",
    "CFIValidationError",
    "EPUBError",
]