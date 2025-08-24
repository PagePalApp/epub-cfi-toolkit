"""
CFI validation functionality for EPUB Canonical Fragment Identifiers.
"""

import re
from typing import Optional, TYPE_CHECKING

from .exceptions import CFIValidationError

# Avoid circular imports
if TYPE_CHECKING:
    from .epub_parser import EPUBParser
    from lxml import etree


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
            r'^(?:epubcfi\()?'  # Optional epubcfi() wrapper
            r'/\d+(?:\[[^\]]+\])?'  # Spine step
            r'(?:/\d+(?:\[[^\]]+\])?)*'  # Additional spine steps
            r'(?:!/?\d+(?:\[[^\]]+\])?(?:/\d+(?:\[[^\]]+\])?)*)?'  # Optional content part
            r'(?::\d+(?:~\d+)?)?'  # Optional text location
            r'(?:\))?$'  # Optional closing paren
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

    def validate_against_document(self, cfi: str, epub_parser: "EPUBParser",
                                  document_tree: Optional["etree._Element"] = None) -> bool:
        """
        Validate a CFI string against the actual document structure.

        Args:
            cfi: The CFI string to validate
            epub_parser: EPUB parser instance for structure validation
            document_tree: Optional document tree for content validation

        Returns:
            True if the CFI is valid and references existing elements, False otherwise
        """
        # First check basic syntax
        if not self.validate(cfi):
            return False

        try:
            from .cfi_parser import CFIParser
            parser = CFIParser()
            parsed_cfi = parser.parse(cfi)

            # Validate spine references
            if not self._validate_spine_references(parsed_cfi, epub_parser):
                return False

            # If we have a document tree, validate content references
            if document_tree is not None:
                if not self._validate_content_references(parsed_cfi, document_tree):
                    return False

            return True

        except Exception:
            return False

    def validate_against_document_strict(self, cfi: str, epub_parser: "EPUBParser",
                                         document_tree: Optional["etree._Element"] = None) -> None:
        """
        Validate a CFI string against document structure and raise detailed exceptions.

        Args:
            cfi: The CFI string to validate
            epub_parser: EPUB parser instance
            document_tree: Optional document tree for content validation

        Raises:
            CFIValidationError: If the CFI is invalid with detailed reason
        """
        # First check basic syntax
        if not self.validate(cfi):
            raise CFIValidationError(f"Invalid CFI format: {cfi}")

        from .cfi_parser import CFIParser
        parser = CFIParser()
        parsed_cfi = parser.parse(cfi)

        # Validate spine references with detailed errors
        self._validate_spine_references_strict(parsed_cfi, epub_parser)

        # If we have a document tree, validate content references
        if document_tree is not None:
            self._validate_content_references_strict(parsed_cfi, document_tree)

    def _validate_spine_references(self, parsed_cfi, epub_parser: "EPUBParser") -> bool:
        """
        Validate that spine references in the CFI exist in the EPUB.
        """
        try:
            # Check if we have enough spine steps
            if len(parsed_cfi.spine_steps) < 2:
                return False

            # Validate the itemref reference (second spine step)
            itemref_step = parsed_cfi.spine_steps[1]
            spine_item = epub_parser.get_spine_item_by_index(itemref_step.index)

            if not spine_item:
                return False

            # Validate assertion if present
            if itemref_step.assertion and spine_item.id != itemref_step.assertion:
                return False

            return True

        except Exception:
            return False

    def _validate_spine_references_strict(self, parsed_cfi, epub_parser: "EPUBParser") -> None:
        """
        Validate spine references with detailed error messages.
        """
        if len(parsed_cfi.spine_steps) < 2:
            raise CFIValidationError("CFI must contain both spine and itemref references")

        # Validate the itemref reference (second spine step)
        itemref_step = parsed_cfi.spine_steps[1]
        spine_item = epub_parser.get_spine_item_by_index(itemref_step.index)

        if not spine_item:
            spine_count = len(epub_parser._spine)
            raise CFIValidationError(
                f"CFI references spine item {itemref_step.index} but document only has {spine_count} spine items "
                f"(valid range: 2-{spine_count * 2})")

        # Validate assertion if present
        if itemref_step.assertion and spine_item.id != itemref_step.assertion:
            raise CFIValidationError(
                f"CFI spine assertion mismatch: expected '{itemref_step.assertion}' but "
                f"spine item {itemref_step.index} has id '{spine_item.id}'")

    def _validate_content_references(self, parsed_cfi, document_tree: "etree._Element") -> bool:
        """
        Validate that content references exist in the document tree.
        """
        try:
            current_element = document_tree

            # Navigate through content steps
            for step in parsed_cfi.content_steps:
                if step.index % 2 == 0:
                    # Even number = element reference
                    child_index = (step.index // 2) - 1
                else:
                    # Odd number = either element or text node reference
                    child_index = (step.index - 1) // 2

                # Check bounds
                if child_index < 0 or child_index >= len(current_element):
                    return False

                # Only navigate to child if it's not the last step with a text node reference
                is_last_step = (step == parsed_cfi.content_steps[-1])
                is_text_node = (step.index % 2 == 1)

                if not (is_last_step and is_text_node):
                    current_element = current_element[child_index]

            # If the last step is a text node reference, validate text node bounds
            if parsed_cfi.content_steps:
                last_step = parsed_cfi.content_steps[-1]
                if last_step.index % 2 == 1:  # Text node reference
                    text_node_index = (last_step.index - 1) // 2
                    text_nodes = self._get_text_nodes(current_element)

                    if text_node_index < 0 or text_node_index >= len(text_nodes):
                        return False

            return True

        except Exception:
            return False

    def _validate_content_references_strict(self, parsed_cfi, document_tree: "etree._Element") -> None:
        """
        Validate content references with detailed error messages.
        """
        current_element = document_tree
        element_path = ["document_root"]

        # Navigate through content steps
        for i, step in enumerate(parsed_cfi.content_steps):
            if step.index % 2 == 0:
                # Even number = element reference
                child_index = (step.index // 2) - 1
                ref_type = "element"
            else:
                # Odd number = either element or text node reference
                child_index = (step.index - 1) // 2
                is_last_step = (i == len(parsed_cfi.content_steps) - 1)
                ref_type = "text node" if (is_last_step and step.index % 2 == 1) else "element"

            # Check bounds
            if child_index < 0:
                raise CFIValidationError(
                    f"Invalid CFI step /{step.index} at position {i+1}: negative index not allowed")

            if child_index >= len(current_element):
                element_name = current_element.tag if hasattr(current_element, 'tag') else 'unknown'
                element_location = ' -> '.join(element_path)
                raise CFIValidationError(
                    f"CFI step /{step.index} references {ref_type} index {child_index} but element "
                    f"<{element_name}> at {element_location} only has {len(current_element)} children "
                    f"(valid range for step: 2-{len(current_element) * 2})")

            # Only navigate to child if it's not the last step with a text node reference
            is_last_step = (i == len(parsed_cfi.content_steps) - 1)
            is_text_node = (step.index % 2 == 1)

            if not (is_last_step and is_text_node):
                current_element = current_element[child_index]
                element_name = current_element.tag if hasattr(current_element, 'tag') else f'child[{child_index}]'
                element_path.append(element_name)

        # If the last step is a text node reference, validate text node bounds
        if parsed_cfi.content_steps:
            last_step = parsed_cfi.content_steps[-1]
            if last_step.index % 2 == 1:  # Text node reference
                text_node_index = (last_step.index - 1) // 2
                text_nodes = self._get_text_nodes(current_element)

                if text_node_index < 0 or text_node_index >= len(text_nodes):
                    element_name = current_element.tag if hasattr(current_element, 'tag') else 'unknown'
                    element_location = ' -> '.join(element_path)
                    raise CFIValidationError(
                        f"CFI step /{last_step.index} references text node index {text_node_index} but element "
                        f"<{element_name}> at {element_location} only has {len(text_nodes)} text nodes")

    def _get_text_nodes(self, element) -> list:
        """
        Get all text nodes within an element (same logic as in CFI processor).
        """
        text_nodes = []

        # Add the element's direct text if it exists
        if hasattr(element, 'text') and element.text:
            text_nodes.append((element, 'text'))

        # Add child elements' tail text
        for child in element:
            if hasattr(child, 'tail') and child.tail:
                text_nodes.append((child, 'tail'))

        return text_nodes
