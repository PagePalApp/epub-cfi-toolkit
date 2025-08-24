"""
CFI parsing functionality for EPUB Canonical Fragment Identifiers.
"""

import re
from typing import List, Optional
from dataclasses import dataclass

from .exceptions import CFIError


@dataclass
class CFIStep:
    """Represents a single step in a CFI path."""
    index: int
    assertion: Optional[str] = None


@dataclass
class CFILocation:
    """Represents a location within a text node."""
    offset: int
    length: Optional[int] = None  # For ranges


@dataclass
class ParsedCFI:
    """Represents a fully parsed CFI."""
    spine_steps: List[CFIStep]
    content_steps: List[CFIStep]
    location: Optional[CFILocation] = None

    @property
    def spine_index(self) -> int:
        """Get the spine index (itemref step, which is typically the second spine step)."""
        if len(self.spine_steps) < 2:
            raise CFIError("CFI must contain both spine and itemref references")
        return self.spine_steps[1].index

    @property
    def spine_assertion(self) -> Optional[str]:
        """Get the spine assertion if present."""
        if len(self.spine_steps) < 2:
            return None
        return self.spine_steps[1].assertion


class CFIParser:
    """Parser for EPUB CFI strings."""

    def __init__(self) -> None:
        """Initialize the CFI parser."""
        # Match CFI components: /step[assertion] or /step:offset or /step:offset~length
        self._step_pattern = re.compile(r'/(\d+)(?:\[([^\]]+)\])?')
        self._location_pattern = re.compile(r':(\d+)(?:~(\d+))?$')

    def parse(self, cfi: str) -> ParsedCFI:
        """
        Parse a CFI string into its components.

        Args:
            cfi: The CFI string to parse (with or without 'epubcfi()' wrapper)

        Returns:
            ParsedCFI object with parsed components

        Raises:
            CFIError: If the CFI cannot be parsed
        """
        if not cfi:
            raise CFIError("CFI cannot be empty")

        # Remove epubcfi() wrapper if present
        cleaned_cfi = self._clean_cfi(cfi)

        # Split into spine and content parts at the '!' separator
        if '!' in cleaned_cfi:
            spine_part, content_part = cleaned_cfi.split('!', 1)
        else:
            spine_part = cleaned_cfi
            content_part = ""

        # Parse spine steps
        spine_steps = self._parse_steps(spine_part)

        # Parse content steps and location
        content_steps = []
        location = None

        if content_part:
            # Check for location offset at the end
            location_match = self._location_pattern.search(content_part)
            if location_match:
                offset = int(location_match.group(1))
                length = int(location_match.group(2)) if location_match.group(2) else None
                location = CFILocation(offset=offset, length=length)
                # Remove location part for step parsing
                content_part = content_part[:location_match.start()]

            content_steps = self._parse_steps(content_part)

        return ParsedCFI(
            spine_steps=spine_steps,
            content_steps=content_steps,
            location=location
        )

    def _clean_cfi(self, cfi: str) -> str:
        """Remove epubcfi() wrapper and validate format."""
        cfi = cfi.strip()

        # Remove epubcfi() wrapper if present
        if cfi.startswith('epubcfi(') and cfi.endswith(')'):
            cfi = cfi[8:-1]

        # Ensure it starts with /
        if not cfi.startswith('/'):
            raise CFIError(f"CFI must start with '/': {cfi}")

        return cfi

    def _parse_steps(self, path_part: str) -> List[CFIStep]:
        """Parse a path part into CFI steps."""
        if not path_part:
            return []

        steps = []
        for match in self._step_pattern.finditer(path_part):
            index = int(match.group(1))
            assertion = match.group(2)
            steps.append(CFIStep(index=index, assertion=assertion))

        return steps

    def compare_cfis(self, cfi1: ParsedCFI, cfi2: ParsedCFI) -> int:
        """
        Compare two parsed CFIs to determine their relative order.

        Returns:
            -1 if cfi1 comes before cfi2
            0 if they are at the same position
            1 if cfi1 comes after cfi2

        Raises:
            CFIError: If CFIs reference different documents
        """
        self._validate_cfis_for_comparison(cfi1, cfi2)

        # Compare spine indices first
        spine_result = self._compare_spine_indices(cfi1, cfi2)
        if spine_result != 0:
            return spine_result

        # Compare content steps
        content_result = self._compare_content_steps(cfi1, cfi2)
        if content_result != 0:
            return content_result

        # Compare locations
        return self._compare_locations(cfi1, cfi2)

    def _validate_cfis_for_comparison(self, cfi1: ParsedCFI, cfi2: ParsedCFI) -> None:
        """Validate that CFIs can be compared."""
        if (len(cfi1.spine_steps) < 2 or len(cfi2.spine_steps) < 2):
            raise CFIError("CFI must contain both spine and itemref references")

    def _compare_spine_indices(self, cfi1: ParsedCFI, cfi2: ParsedCFI) -> int:
        """Compare spine indices of two CFIs."""
        idx1, idx2 = cfi1.spine_steps[1].index, cfi2.spine_steps[1].index
        if idx1 < idx2:
            return -1
        elif idx1 > idx2:
            return 1
        return 0

    def _compare_content_steps(self, cfi1: ParsedCFI, cfi2: ParsedCFI) -> int:
        """Compare content steps of two CFIs."""
        min_steps = min(len(cfi1.content_steps), len(cfi2.content_steps))

        for i in range(min_steps):
            idx1, idx2 = cfi1.content_steps[i].index, cfi2.content_steps[i].index
            if idx1 < idx2:
                return -1
            elif idx1 > idx2:
                return 1

        # Compare by number of steps if all compared steps are equal
        len1, len2 = len(cfi1.content_steps), len(cfi2.content_steps)
        if len1 < len2:
            return -1
        elif len1 > len2:
            return 1
        return 0

    def _compare_locations(self, cfi1: ParsedCFI, cfi2: ParsedCFI) -> int:
        """Compare locations of two CFIs."""
        if cfi1.location and cfi2.location:
            if cfi1.location.offset < cfi2.location.offset:
                return -1
            elif cfi1.location.offset > cfi2.location.offset:
                return 1
            return 0
        elif cfi1.location is None and cfi2.location is None:
            return 0
        elif cfi1.location is None:
            return -1
        else:
            return 1
