"""
Tests for the CFI processor.
"""

import pytest
from pathlib import Path

from epub_cfi_toolkit import CFIProcessor, EPUBError, CFIError


class TestCFIProcessor:
    """Test cases for the CFIProcessor class."""
    
    def test_init_nonexistent_file(self):
        """Test initialization with non-existent EPUB file."""
        with pytest.raises(EPUBError, match="EPUB file not found"):
            CFIProcessor("nonexistent.epub")
    
    def test_init_valid_epub(self):
        """Test initialization with valid EPUB file."""
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        processor = CFIProcessor(str(epub_path))
        
        # Test that the processor was initialized with required components
        assert processor.cfi_parser is not None
        assert processor.epub_parser is not None
    
    def test_extract_text_from_cfi_range_functionality(self):
        """Test that extract_text_from_cfi_range works correctly."""
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        processor = CFIProcessor(str(epub_path))
        
        # Test basic functionality with a simple CFI range
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:3)"
        
        result = processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "xxx"
    
    def test_invalid_cfi_validation(self):
        """Test that invalid CFIs raise appropriate errors."""
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        processor = CFIProcessor(str(epub_path))
        
        invalid_cfi = "invalid_cfi_format"
        valid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        
        with pytest.raises(CFIError):
            processor.extract_text_from_cfi_range(invalid_cfi, valid_cfi)
    
