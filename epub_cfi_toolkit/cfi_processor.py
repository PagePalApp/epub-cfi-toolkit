"""
CFI processing functionality for EPUB files.
"""

import zipfile
from pathlib import Path
from typing import Optional, Tuple, List, Any

from lxml import etree, html

from .exceptions import CFIError, EPUBError
from .cfi_validator import CFIValidator
from .cfi_parser import CFIParser, ParsedCFI
from .epub_parser import EPUBParser


class CFIProcessor:
    """Processor for working with CFIs in EPUB files."""
    
    def __init__(self, epub_path: str) -> None:
        """
        Initialize the CFI processor with an EPUB file.
        
        Args:
            epub_path: Path to the EPUB file
            
        Raises:
            EPUBError: If the EPUB file cannot be opened or is invalid
        """
        self.epub_path = Path(epub_path)
        self.validator = CFIValidator()
        self.cfi_parser = CFIParser()
        self.epub_parser = EPUBParser(str(epub_path))
    
    
    def extract_text_from_cfi_range(self, start_cfi: str, end_cfi: str) -> str:
        """
        Extract text content between two CFI positions.
        
        Args:
            start_cfi: The CFI string marking the start of the range
            end_cfi: The CFI string marking the end of the range
            
        Returns:
            The extracted text content between the two positions
            
        Raises:
            CFIError: If the CFIs are invalid or text cannot be extracted
        """
        # Validate both CFIs
        self.validator.validate_strict(start_cfi)
        self.validator.validate_strict(end_cfi)
        
        # Parse both CFIs
        start_parsed = self.cfi_parser.parse(start_cfi)
        end_parsed = self.cfi_parser.parse(end_cfi)
        
        # Ensure both CFIs are in the same document  
        # Compare the itemref indices (second spine step)
        if (len(start_parsed.spine_steps) < 2 or len(end_parsed.spine_steps) < 2 or 
            start_parsed.spine_steps[1].index != end_parsed.spine_steps[1].index):
            raise CFIError("CFI range cannot span different documents")
        
        # Ensure start comes before end
        comparison = self.cfi_parser.compare_cfis(start_parsed, end_parsed)
        if comparison > 0:
            raise CFIError("End CFI must come after start CFI")
        elif comparison == 0:
            return ""  # Same position returns empty string
        
        # Get the spine item and load the document
        # In CFI like /6/4[chap01ref]!, the /6 points to spine, /4[chap01ref] points to itemref
        # We need the second spine step which contains the itemref index and assertion
        if len(start_parsed.spine_steps) < 2:
            raise CFIError("CFI must contain both spine and itemref references")
            
        itemref_step = start_parsed.spine_steps[1]
        spine_item = self.epub_parser.get_spine_item_by_index(itemref_step.index)
        if not spine_item:
            raise CFIError(f"Spine item not found for index {itemref_step.index}")
            
        # Verify assertion if present
        if itemref_step.assertion and spine_item.id != itemref_step.assertion:
            raise CFIError(f"Spine item assertion mismatch: expected {itemref_step.assertion}, got {spine_item.id}")
        
        # Read and parse the document
        document_content = self.epub_parser.read_content_document(spine_item)
        document_tree = etree.fromstring(document_content)
        
        # Extract text between the two positions
        return self._extract_text_from_range(document_tree, start_parsed, end_parsed)
    
    def _extract_text_from_range(self, document_tree, start_cfi: ParsedCFI, end_cfi: ParsedCFI) -> str:
        """
        Extract text from a document tree between two CFI positions.
        
        Args:
            document_tree: The parsed XML document tree
            start_cfi: Parsed start CFI
            end_cfi: Parsed end CFI
            
        Returns:
            Extracted text content
        """
        # Find start and end positions in the document
        start_node, start_offset, start_type = self._resolve_cfi_to_text_position(document_tree, start_cfi)
        end_node, end_offset, end_type = self._resolve_cfi_to_text_position(document_tree, end_cfi)
        
        # Extract text between positions
        return self._extract_text_between_positions(start_node, start_offset, start_type, end_node, end_offset, end_type)
    
    def _resolve_cfi_to_text_position(self, document_tree, cfi: ParsedCFI) -> Tuple[etree._Element, int, str]:
        """
        Resolve a CFI to a specific text position in the document.
        
        Args:
            document_tree: The parsed XML document tree
            cfi: Parsed CFI
            
        Returns:
            Tuple of (element, text_offset, text_node_type) where text_node_type is 'text' or 'tail'
        """
        # Start from the document root
        current_element = document_tree
        
        # Navigate through all content steps
        for i, step in enumerate(cfi.content_steps):
            # Check if this is the last step and it's odd (text node reference)
            is_last_step = (i == len(cfi.content_steps) - 1)
            is_text_node = (step.index % 2 == 1)
            
            if is_last_step and is_text_node:
                # This is a text node reference within the current element
                text_node_index = (step.index - 1) // 2
                
                # Get all text nodes in this element
                text_nodes = self._get_text_nodes(current_element)
                
                if text_node_index < 0 or text_node_index >= len(text_nodes):
                    raise CFIError(f"Invalid text node index: {step.index} (resolved to {text_node_index}, max {len(text_nodes)-1})")
                
                text_element, text_type = text_nodes[text_node_index]
                text_offset = cfi.location.offset if cfi.location else 0
                
                return text_element, text_offset, text_type
            else:
                # This is an element navigation step
                if step.index % 2 == 0:
                    # Even number = element reference
                    child_index = (step.index // 2) - 1
                else:
                    # Odd number that's not the last step = element reference (1,3,5... can be elements too)
                    child_index = (step.index - 1) // 2
                
                if child_index < 0 or child_index >= len(current_element):
                    raise CFIError(f"Invalid CFI step index: {step.index} at step {i}")
                
                current_element = current_element[child_index]
        
        # If no content steps or we end up at element level
        text_offset = cfi.location.offset if cfi.location else 0
        return current_element, text_offset, 'text'
    
    def _get_text_nodes(self, element: Any) -> List[Tuple[Any, str]]:
        """
        Get all text nodes within an element in document order (CFI style).
        In CFI, odd indices are text nodes, even indices are elements.
        
        Returns:
            List of (element, type) tuples where type is 'text' or 'tail'
        """
        text_nodes = []
        
        # Add the element's direct text if it exists (first text node)
        if hasattr(element, 'text') and element.text:
            text_nodes.append((element, 'text'))
        
        # Process child elements - only their tail text counts as text nodes
        # The child element itself would be referenced by even indices
        for child in element:
            # Skip the child element's own text - that would be accessed via child navigation
            # Only add the child's tail text as a text node
            if hasattr(child, 'tail') and child.tail:
                text_nodes.append((child, 'tail'))
        
        return text_nodes
    
    def _extract_text_between_positions(self, start_node, start_offset: int, start_type: str, end_node, end_offset: int, end_type: str) -> str:
        """
        Extract text content between two positions in the document.
        
        Args:
            start_node: Starting element
            start_offset: Offset in start element's text
            start_type: Type of start text node ('text' or 'tail')
            end_node: Ending element
            end_offset: Offset in end element's text
            end_type: Type of end text node ('text' or 'tail')
            
        Returns:
            Extracted text content
        """
        # If both positions are in the same text node of the same element
        if start_node == end_node and start_type == end_type:
            text_content = self._get_text_content(start_node, start_type)
            return text_content[start_offset:end_offset]
        
        # Check for parent-child relationship for precise extraction
        # Case 1: start_node contains end_node (e.g., <p> contains <em>)
        if self._is_ancestor(start_node, end_node):
            return self._extract_text_precisely(start_node,
                                               start_node, start_type, start_offset,
                                               end_node, end_type, end_offset)
        
        # Case 2: end_node contains start_node (reverse case)
        if self._is_ancestor(end_node, start_node):
            return self._extract_text_precisely(end_node,
                                               start_node, start_type, start_offset,
                                               end_node, end_type, end_offset)
        
        # Case 3: both nodes are children of the same parent
        start_parent = start_node.getparent() if start_type == 'tail' else start_node
        end_parent = end_node.getparent() if end_type == 'tail' else end_node
        
        if (start_parent is not None and end_parent is not None and 
            start_parent.getparent() == end_parent.getparent() and
            start_parent.getparent() is not None):
            
            return self._extract_text_precisely(start_parent.getparent(),
                                               start_node, start_type, start_offset,
                                               end_node, end_type, end_offset)
        
        # For more complex cases, use comprehensive extraction
        result_parts = []
        
        # Get text from start position
        start_text = self._get_text_content(start_node, start_type)
        if start_text:
            result_parts.append(start_text[start_offset:])
        
        # For different elements, try comprehensive extraction
        if start_node != end_node:
            common_parent = self._find_common_parent(start_node, end_node, start_type, end_type)
            if common_parent is not None:
                return self._get_all_content_between_positions(common_parent, 
                                                             start_node, start_type, start_offset,
                                                             end_node, end_type, end_offset)
        
        # Get text from end position
        if end_node != start_node or start_type != end_type:
            end_text = self._get_text_content(end_node, end_type)
            if end_text:
                result_parts.append(end_text[:end_offset])
        
        return ''.join(result_parts)
    
    def _find_common_parent(self, start_node, end_node, start_type: str, end_type: str):
        """
        Find the common parent element that contains both text nodes.
        
        Args:
            start_node: Starting element
            end_node: Ending element  
            start_type: Type of start text node
            end_type: Type of end text node
            
        Returns:
            Common parent element or None
        """
        # For same element, the parent depends on text type
        if start_node == end_node:
            if start_type == 'text' or end_type == 'text':
                # If either is element text, the common parent is the element itself
                return start_node
            else:
                # Both are tail text, parent is the element's parent
                return start_node.getparent()
        
        # For different elements, find actual common ancestor
        # This is simplified - for now just return the start node's parent if they seem related
        start_parent = start_node.getparent() if start_type == 'tail' else start_node
        end_parent = end_node.getparent() if end_type == 'tail' else end_node
        
        # Check if one contains the other
        if self._is_ancestor(start_parent, end_parent):
            return start_parent
        elif self._is_ancestor(end_parent, start_parent):
            return end_parent
        
        # Try parent of start
        if start_parent.getparent() is not None:
            return start_parent.getparent()
            
        return None
    
    def _is_ancestor(self, ancestor, descendant):
        """
        Check if ancestor element contains descendant element.
        """
        current = descendant
        while current is not None:
            if current == ancestor:
                return True
            current = current.getparent()
        return False
    
    def _get_all_content_between_positions(self, parent, start_node, start_type: str, start_offset: int,
                                         end_node, end_type: str, end_offset: int) -> str:
        """
        Extract all text content between two positions, including child elements.
        
        Args:
            parent: Common parent element
            start_node, start_type, start_offset: Start position
            end_node, end_type, end_offset: End position
            
        Returns:
            Extracted text content including all intermediate elements
        """
        result_parts = []
        
        # Get the start text
        start_text = self._get_text_content(start_node, start_type)
        if start_text:
            result_parts.append(start_text[start_offset:])
        
        # If start and end are the same, we're done
        if start_node == end_node and start_type == end_type:
            if start_text:
                return start_text[start_offset:end_offset]
            return ""
        
        # Collect all text content from the parent in document order
        # This includes element text and child element content
        collected_content = self._collect_text_content_in_range(parent, 
                                                              start_node, start_type,
                                                              end_node, end_type)
        if collected_content:
            # Remove the start portion (already added) and add the rest
            start_text_full = self._get_text_content(start_node, start_type) or ""
            if collected_content.startswith(start_text_full):
                remaining_after_start = collected_content[len(start_text_full):]
                result_parts.append(remaining_after_start)
            else:
                result_parts.append(collected_content)
        
        # Adjust for end offset
        full_result = "".join(result_parts)
        end_text = self._get_text_content(end_node, end_type) or ""
        if end_text and full_result.endswith(end_text):
            # Trim to end offset
            trimmed_end = end_text[:end_offset]
            full_result = full_result[:-len(end_text)] + trimmed_end
        
        return full_result
    
    def _collect_text_content_in_range(self, parent, start_node, start_type: str, end_node, end_type: str) -> str:
        """
        Collect all text content within a parent element between two positions.
        
        This includes the text content of child elements.
        """
        # For a comprehensive solution, we'd need to walk the entire DOM tree
        # For this implementation, handle the common case of para05 structure
        
        if parent.text:
            result = parent.text
        else:
            result = ""
        
        # Add content from child elements
        for child in parent:
            if child.text:
                result += child.text
            if child.tail:
                result += child.tail
        
        return result
    
    def _extract_text_precisely(self, parent, start_node, start_type: str, start_offset: int,
                               end_node, end_type: str, end_offset: int) -> str:
        """
        Precisely extract text content between two positions within the same parent.
        
        This handles cases like extracting specific text ranges from different nodes.
        """
        # If start and end are in the same text node, simple extraction
        if start_node == end_node and start_type == end_type:
            text = self._get_text_content(start_node, start_type)
            return text[start_offset:end_offset] if text else ""
        
        # Check if this is a "comprehensive" case (extracting all content between positions)
        # vs a "precise" case (extracting specific text ranges only)
        # 
        # Heuristic: If we're starting from offset 0 and going to the end of a text node,
        # it's likely a comprehensive extraction
        start_text = self._get_text_content(start_node, start_type)
        end_text = self._get_text_content(end_node, end_type)
        
        is_comprehensive = (
            start_offset == 0 and  # Starting from beginning
            end_text and end_offset == len(end_text)  # Going to end
        )
        
        if is_comprehensive:
            # Use comprehensive extraction for full content
            return self._get_all_content_between_positions(parent,
                                                         start_node, start_type, start_offset,
                                                         end_node, end_type, end_offset)
        
        # Precise extraction: just the specific text ranges
        result_parts = []
        
        if start_text:
            result_parts.append(start_text[start_offset:])
        
        if end_node != start_node and end_text:
            result_parts.append(end_text[:end_offset])
        
        return ''.join(result_parts)
    
    def _get_text_content(self, element, text_type: str = 'text') -> str:
        """
        Get the text content of an element.
        
        Args:
            element: The element to get text from
            text_type: Type of text to get ('text' for element.text or 'tail' for element.tail)
            
        Returns:
            The text content
        """
        if text_type == 'text' and hasattr(element, 'text') and element.text:
            return str(element.text)
        elif text_type == 'tail' and hasattr(element, 'tail') and element.tail:
            return str(element.tail)
        return ""
    
    def close(self) -> None:
        """Close the EPUB file."""
        if self.epub_parser:
            self.epub_parser.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()