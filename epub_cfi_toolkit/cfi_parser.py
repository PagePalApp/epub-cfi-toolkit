"""
CFI parsing functionality for EPUB Canonical Fragment Identifiers.
"""

import re
from dataclasses import dataclass
from typing import List, Optional

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
        """Get the spine index (itemref step, typically second spine step)."""
        if len(self.spine_steps) < 2:
            raise CFIError(
                "CFI must contain both spine and itemref references"
            )
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
        # Match CFI components: /step[assertion] or /step:offset or
        # /step:offset~length
        self._step_pattern = re.compile(r"/(\d+)(?:\[([^\]]+)\])?")
        self._location_pattern = re.compile(r":(\d+)(?:~(\d+))?$")

        # Characters that need to be escaped with circumflex (^) per CFI spec
        self._escape_chars = {"[", "]", "^", ",", "(", ")", ";"}

    def parse(self, cfi: str) -> ParsedCFI:
        """
        Parse a CFI string into its components.

        Args:
            cfi: The CFI string to parse (with or without 'epubcfi()' wrapper)
                Can be a simple CFI or range CFI with comma syntax

        Returns:
            ParsedCFI object with parsed components

        Raises:
            CFIError: If the CFI cannot be parsed
        """
        if not cfi:
            raise CFIError("CFI cannot be empty")

        # Check if this is a range CFI with comma syntax
        if self._is_range_cfi(cfi):
            return self._parse_range_cfi(cfi)

        # Parse as simple CFI
        return self._parse_simple_cfi(cfi)

    def _is_range_cfi(self, cfi: str) -> bool:
        """Check if CFI uses range syntax with commas."""
        # Range CFI has format: epubcfi(parent, start, end)
        cleaned = cfi.strip()
        if cleaned.startswith("epubcfi(") and cleaned.endswith(")"):
            inner = cleaned[8:-1]
            # Count non-escaped commas
            comma_count = 0
            i = 0
            while i < len(inner):
                if inner[i] == "," and (i == 0 or inner[i - 1] != "^"):
                    comma_count += 1
                i += 1
            return comma_count == 2
        return False

    def _parse_range_cfi(self, cfi: str) -> ParsedCFI:
        """Parse a range CFI with comma syntax: epubcfi(parent, start, end)."""
        # Extract inner content
        inner = cfi.strip()[8:-1]  # Remove epubcfi( and )

        # Split by non-escaped commas
        parts = []
        current_part: List[str] = []
        i = 0
        while i < len(inner):
            if inner[i] == "," and (i == 0 or inner[i - 1] != "^"):
                parts.append("".join(current_part).strip())
                current_part = []
            else:
                current_part.append(inner[i])
            i += 1
        parts.append("".join(current_part).strip())

        if len(parts) != 3:
            raise CFIError(
                "Range CFI must have exactly 3 parts: parent, start, end")

        parent_path, start_subpath, end_subpath = parts

        # For now, we'll parse the start subpath as the main CFI
        # A full implementation would need to handle the range semantics
        # properly
        full_start_cfi = parent_path + start_subpath
        return self._parse_simple_cfi(full_start_cfi)

    def _parse_simple_cfi(self, cfi: str) -> ParsedCFI:
        """Parse a simple (non-range) CFI."""
        # Remove epubcfi() wrapper if present
        cleaned_cfi = self._clean_cfi(cfi)

        # Split into spine and content parts at the '!' separator
        if "!" in cleaned_cfi:
            spine_part, content_part = cleaned_cfi.split("!", 1)
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
                length = (
                    int(location_match.group(2)
                        ) if location_match.group(2) else None
                )
                location = CFILocation(offset=offset, length=length)
                # Remove location part for step parsing
                content_part = content_part[: location_match.start()]

            content_steps = self._parse_steps(content_part)

        return ParsedCFI(
            spine_steps=spine_steps, content_steps=content_steps, location=location
        )

    def _clean_cfi(self, cfi: str) -> str:
        """Remove epubcfi() wrapper, handle escaping, and validate format."""
        cfi = cfi.strip()

        # Remove epubcfi() wrapper if present
        if cfi.startswith("epubcfi(") and cfi.endswith(")"):
            cfi = cfi[8:-1]

        # Handle character escaping
        cfi = self._unescape_cfi(cfi)

        # Ensure it starts with /
        if not cfi.startswith("/"):
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

    def _unescape_cfi(self, cfi: str) -> str:
        """
        Unescape CFI string by processing circumflex (^) escape sequences.

        Per CFI spec, these characters must be escaped: [ ] ^ , ( ) ;
        """
        result = []
        i = 0
        while i < len(cfi):
            char = cfi[i]
            if char == "^" and i + 1 < len(cfi):
                # Found escape sequence
                next_char = cfi[i + 1]
                if next_char in self._escape_chars:
                    # Valid escape sequence
                    result.append(next_char)
                    i += 2  # Skip both ^ and the escaped character
                else:
                    # Invalid escape sequence - treat ^ as literal
                    result.append(char)
                    i += 1
            else:
                result.append(char)
                i += 1

        return "".join(result)

    def _escape_cfi(self, cfi: str) -> str:
        """
        Escape CFI string by adding circumflex (^) before special characters.

        This is used when generating CFI strings.
        """
        result = []
        for char in cfi:
            if char in self._escape_chars:
                result.append("^" + char)
            else:
                result.append(char)
        return "".join(result)

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
        # Must be in the same spine item (compare itemref indices)
        if len(cfi1.spine_steps) < 2 or len(cfi2.spine_steps) < 2:
            raise CFIError(
                "CFI must contain both spine and itemref references")

        if cfi1.spine_steps[1].index != cfi2.spine_steps[1].index:
            if cfi1.spine_steps[1].index < cfi2.spine_steps[1].index:
                return -1
            else:
                return 1

        # Compare content steps
        min_steps = min(len(cfi1.content_steps), len(cfi2.content_steps))

        for i in range(min_steps):
            if cfi1.content_steps[i].index < cfi2.content_steps[i].index:
                return -1
            elif cfi1.content_steps[i].index > cfi2.content_steps[i].index:
                return 1

        # If all compared steps are equal, compare by number of steps
        if len(cfi1.content_steps) < len(cfi2.content_steps):
            return -1
        elif len(cfi1.content_steps) > len(cfi2.content_steps):
            return 1

        # Same path, compare locations
        if cfi1.location and cfi2.location:
            if cfi1.location.offset < cfi2.location.offset:
                return -1
            elif cfi1.location.offset > cfi2.location.offset:
                return 1
            else:
                return 0
        elif cfi1.location is None and cfi2.location is None:
            return 0
        elif cfi1.location is None:
            return -1
        else:
            return 1
