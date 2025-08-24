"""
Exception classes for the EPUB CFI Toolkit.
"""


class CFIError(Exception):
    """Base exception class for CFI-related errors."""
    pass


class CFIValidationError(CFIError):
    """Exception raised when CFI validation fails."""
    pass


class EPUBError(Exception):
    """Base exception class for EPUB-related errors."""
    pass