"""
Tests for enhanced CFI validation features.
"""

import pytest
from pathlib import Path
from epub_cfi_toolkit import CFIProcessor, CFIValidator, CFIError, CFIValidationError


class TestEnhancedCFIValidation:
    """Test cases for enhanced CFI validation features."""
    
    def setup_method(self):
        """Set up test fixtures."""
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        self.processor = CFIProcessor(str(epub_path))
        self.validator = CFIValidator()
    
    def teardown_method(self):
        """Clean up after tests."""
        self.processor.close()
    
    def test_validate_against_document_valid_cfi(self):
        """Test validation of valid CFI against document structure."""
        valid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        
        # Parse to get document tree for validation
        parsed_cfi = self.processor.cfi_parser.parse(valid_cfi)
        itemref_step = parsed_cfi.spine_steps[1]
        spine_item = self.processor.epub_parser.get_spine_item_by_index(itemref_step.index)
        document_content = self.processor.epub_parser.read_content_document(spine_item)
        
        from lxml import etree
        document_tree = etree.fromstring(document_content)
        
        # Should validate successfully
        assert self.validator.validate_against_document(valid_cfi, self.processor.epub_parser, document_tree)
    
    def test_validate_against_document_invalid_spine_reference(self):
        """Test validation fails for invalid spine reference."""
        invalid_cfi = "epubcfi(/6/50[nonexistent]!/4[body01]/10[para05]/1:0)"  # /50 doesn't exist
        
        # Should fail validation
        assert not self.validator.validate_against_document(invalid_cfi, self.processor.epub_parser, None)
    
    def test_validate_against_document_strict_detailed_error(self):
        """Test strict validation provides detailed error messages."""
        invalid_cfi = "epubcfi(/6/50[nonexistent]!/4[body01]/10[para05]/1:0)"
        
        with pytest.raises(CFIValidationError) as excinfo:
            self.validator.validate_against_document_strict(invalid_cfi, self.processor.epub_parser, None)
        
        # Error should mention spine item count and valid range
        error_message = str(excinfo.value)
        assert "spine item 50" in error_message
        assert "valid range" in error_message
    
    def test_validate_against_document_invalid_element_reference(self):
        """Test validation fails for invalid element references."""
        # This CFI references element that doesn't exist in the document
        invalid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/50[nonexistent]/1:0)"
        
        # Parse to get document tree
        valid_spine_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        parsed_cfi = self.processor.cfi_parser.parse(valid_spine_cfi)
        itemref_step = parsed_cfi.spine_steps[1]
        spine_item = self.processor.epub_parser.get_spine_item_by_index(itemref_step.index)
        document_content = self.processor.epub_parser.read_content_document(spine_item)
        
        from lxml import etree
        document_tree = etree.fromstring(document_content)
        
        # Should fail validation
        assert not self.validator.validate_against_document(invalid_cfi, self.processor.epub_parser, document_tree)
    
    def test_validate_against_document_strict_element_error_details(self):
        """Test strict validation provides detailed error messages for invalid elements."""
        invalid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/50[nonexistent]/1:0)"
        
        # Get document tree
        valid_spine_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        parsed_cfi = self.processor.cfi_parser.parse(valid_spine_cfi)
        itemref_step = parsed_cfi.spine_steps[1]
        spine_item = self.processor.epub_parser.get_spine_item_by_index(itemref_step.index)
        document_content = self.processor.epub_parser.read_content_document(spine_item)
        
        from lxml import etree
        document_tree = etree.fromstring(document_content)
        
        with pytest.raises(CFIValidationError) as excinfo:
            self.validator.validate_against_document_strict(invalid_cfi, self.processor.epub_parser, document_tree)
        
        # Error should mention element information and valid ranges
        error_message = str(excinfo.value)
        assert "step /50" in error_message
        assert "only has" in error_message
        assert "children" in error_message
    
    def test_cfi_bounds_validation_methods(self):
        """Test the new CFI bounds validation methods."""
        valid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        invalid_cfi = "epubcfi(/6/50[nonexistent]!/4[body01]/10[para05]/1:0)"
        
        # Test bounds validation methods
        assert self.processor.validate_cfi_bounds(valid_cfi)
        assert not self.processor.validate_cfi_bounds(invalid_cfi)
    
    def test_cfi_bounds_validation_strict_methods(self):
        """Test strict CFI bounds validation methods."""
        valid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        invalid_cfi = "epubcfi(/6/50[nonexistent]!/4[body01]/10[para05]/1:0)"
        
        # Valid CFI should pass
        self.processor.validate_cfi_bounds_strict(valid_cfi)  # Should not raise
        
        # Invalid CFI should raise with detailed message
        with pytest.raises(CFIError) as excinfo:
            self.processor.validate_cfi_bounds_strict(invalid_cfi)
        
        error_message = str(excinfo.value)
        assert ("CFI validation failed" in error_message or 
                "Spine item not found" in error_message)
    
    def test_enhanced_error_message_for_reversed_cfi_order(self):
        """Test improved error message for reversed CFI order."""
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:20)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"  # Before start
        
        with pytest.raises(CFIError) as excinfo:
            self.processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        
        # Should provide helpful error message about swapping CFIs
        error_message = str(excinfo.value)
        assert "reverse order" in error_message
        assert "swap" in error_message
        assert start_cfi in error_message
        assert end_cfi in error_message
    
    def test_validation_during_text_extraction(self):
        """Test that validation occurs during text extraction."""
        valid_start = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        invalid_end = "epubcfi(/6/4[chap01ref]!/4[body01]/50[nonexistent]/1:0)"  # Invalid element
        
        # Should fail with validation error during extraction
        with pytest.raises(CFIError) as excinfo:
            self.processor.extract_text_from_cfi_range(valid_start, invalid_end)
        
        error_message = str(excinfo.value)
        assert ("CFI validation failed" in error_message or 
                "Spine item not found" in error_message)
    
    def test_text_node_validation(self):
        """Test validation of text node references."""
        # CFI that references a text node index that doesn't exist
        invalid_text_node_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/99:0)"  # Text node 99 doesn't exist
        
        assert not self.processor.validate_cfi_bounds(invalid_text_node_cfi)
        
        with pytest.raises(CFIError):
            self.processor.validate_cfi_bounds_strict(invalid_text_node_cfi)
    
    def test_assertion_mismatch_validation(self):
        """Test validation of CFI assertions."""
        # CFI with wrong assertion
        wrong_assertion_cfi = "epubcfi(/6/4[wrong_assertion]!/4[body01]/10[para05]/1:0)"
        
        with pytest.raises(CFIError) as excinfo:
            self.processor.validate_cfi_bounds_strict(wrong_assertion_cfi)
        
        error_message = str(excinfo.value)
        assert "assertion mismatch" in error_message or "CFI validation failed" in error_message


class TestImprovedErrorMessages:
    """Test improved error messages for various CFI issues."""
    
    def setup_method(self):
        """Set up test fixtures."""
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        self.processor = CFIProcessor(str(epub_path))
    
    def teardown_method(self):
        """Clean up after tests."""
        self.processor.close()
    
    def test_helpful_spine_reference_error(self):
        """Test that spine reference errors are helpful."""
        invalid_spine_cfi = "epubcfi(/6/100!/4[body01]/10[para05]/1:0)"
        
        with pytest.raises(CFIError) as excinfo:
            self.processor.extract_text_from_cfi_range(invalid_spine_cfi, invalid_spine_cfi)
        
        error_message = str(excinfo.value)
        # Should mention valid range for spine items
        assert ("valid range" in error_message or 
                "spine item" in error_message or
                "CFI validation failed" in error_message)
    
    def test_helpful_element_reference_error(self):
        """Test that element reference errors are helpful."""
        invalid_element_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/100[nonexistent]/1:0)"
        
        with pytest.raises(CFIError) as excinfo:
            self.processor.extract_text_from_cfi_range(invalid_element_cfi, invalid_element_cfi)
        
        error_message = str(excinfo.value)
        # Should mention element information
        assert ("children" in error_message or 
                "element" in error_message or
                "CFI validation failed" in error_message)