"""
CFI validation functionality for EPUB Canonical Fragment Identifiers.
"""

import re

from .exceptions import CFIValidationError


class CFIValidator:
    """Validator for EPUB Canonical Fragment Identifiers (CFIs)."""
    
    def __init__(self) -> None:
        """Initialize the CFI validator."""
        # Enhanced CFI pattern that properly handles the epubcfi() wrapper and text offsets
        # Pattern explanation:
        # - Optional epubcfi() wrapper
        # - Spine part: /\d+(\[\w+\])? (may repeat)
        # - Optional content part after ! 
        # - Optional text location :offset or :offset~length
        self._cfi_pattern = re.compile(
            r'^(?:epubcfi\()?/\d+(?:\[[^\]]+\])?(?:/\d+(?:\[[^\]]+\])?)*(?:!/?\d+(?:\[[^\]]+\])?(?:/\d+(?:\[[^\]]+\])?)*)?(?::\d+(?:~\d+)?)?(?:\))?$'
        )
    
    def validate(self, cfi: str) -> bool:
        """
        Validate a CFI string for correct syntax.
        
        Args:
            cfi: The CFI string to validate
            
        Returns:
            True if the CFI is valid, False otherwise
        """
        if not cfi:
            return False
        
        if not isinstance(cfi, str):
            return False
        
        # Check basic pattern match
        return bool(self._cfi_pattern.match(cfi))
    
    def validate_strict(self, cfi: str) -> None:
        """
        Validate a CFI string and raise an exception if invalid.
        
        Args:
            cfi: The CFI string to validate
            
        Raises:
            CFIValidationError: If the CFI is invalid
        """
        if not self.validate(cfi):
            raise CFIValidationError(f"Invalid CFI format: {cfi}")