"""
Tests for CFI range text extraction functionality.
Based on the EPUB CFI specification examples.
"""

import pytest
from pathlib import Path

from epub_cfi_toolkit import CFIProcessor, CFIError


class TestCFIRangeExtraction:
    """Test cases for extracting text from CFI ranges."""
    
    @pytest.fixture
    def sample_epub_path(self):
        """Return path to sample EPUB file."""
        return Path(__file__).parent.parent / "test_data" / "sample.epub"
    
    @pytest.fixture
    def cfi_processor(self, sample_epub_path):
        """Return CFI processor instance."""
        return CFIProcessor(str(sample_epub_path))
    
    def test_extract_single_character(self, cfi_processor):
        """Test extracting a single character using CFI range."""
        # Extract just the character "9" from "0123456789"
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:9)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)"
        
        result = cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "9"
    
    def test_extract_multiple_characters(self, cfi_processor):
        """Test extracting multiple characters using CFI range."""
        # Extract "789" from "0123456789"
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:7)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)"
        
        result = cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "789"
    
    def test_extract_from_text_node_start(self, cfi_processor):
        """Test extracting from the start of a text node."""
        # Extract "xxx" from the beginning of para05
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:3)"
        
        result = cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "xxx"
    
    def test_extract_from_em_element(self, cfi_processor):
        """Test extracting text from within an em element."""
        # Extract "yyy" from the em element
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/2/1:0)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/2/1:3)"
        
        result = cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "yyy"
    
    def test_extract_across_elements(self, cfi_processor):
        """Test extracting text that spans across elements."""
        # Extract from "xx" in xxx through "yy" in yyy
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:1)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/2/1:2)"
        
        result = cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "xxyy"
    
    def test_extract_full_paragraph_content(self, cfi_processor):
        """Test extracting the full content of a paragraph."""
        # Extract entire content of para05: "xxx" + "yyy" + "0123456789"
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)"
        
        result = cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "xxxyyy0123456789"
    
    def test_extract_across_paragraphs(self, cfi_processor):
        """Test extracting text across multiple paragraphs."""
        # Extract from middle of para05 to start of next paragraph
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:5)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/12[para06]/1:6)"
        
        result = cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        # Should extract "56789" + paragraph break + "Sixth "
        expected = "56789Sixth "  # Simplified - actual implementation may handle whitespace differently
        assert result == expected
    
    def test_invalid_cfi_range(self, cfi_processor):
        """Test that invalid CFI ranges raise appropriate errors."""
        invalid_cfi = "invalid_cfi_format"
        valid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        
        with pytest.raises(CFIError):
            cfi_processor.extract_text_from_cfi_range(invalid_cfi, valid_cfi)
    
    def test_cfi_range_different_documents(self, cfi_processor):
        """Test that CFI range spanning different documents raises error."""
        cfi_chap01 = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        cfi_chap02 = "epubcfi(/6/6[chap02ref]!/4[body02]/2[para01]/1:5)"
        
        with pytest.raises(CFIError, match="CFI range cannot span different documents"):
            cfi_processor.extract_text_from_cfi_range(cfi_chap01, cfi_chap02)
    
    def test_reverse_cfi_range(self, cfi_processor):
        """Test that reversed CFI range (end before start) raises error."""
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:5)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:2)"
        
        with pytest.raises(CFIError, match="End CFI must come after start CFI"):
            cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
    
    def test_same_position_cfi_range(self, cfi_processor):
        """Test CFI range where start and end are the same position."""
        same_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:5)"
        
        result = cfi_processor.extract_text_from_cfi_range(same_cfi, same_cfi)
        assert result == ""  # Should return empty string for same position