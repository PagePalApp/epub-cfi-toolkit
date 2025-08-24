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
        assert processor.validator is not None
        
        processor.close()
    
    def test_extract_text_from_cfi_range_functionality(self):
        """Test that extract_text_from_cfi_range works correctly."""
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        processor = CFIProcessor(str(epub_path))
        
        # Test basic functionality with a simple CFI range
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:3)"
        
        result = processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "xxx"
        
        processor.close()
    
    def test_invalid_cfi_validation(self):
        """Test that invalid CFIs raise appropriate errors."""
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        processor = CFIProcessor(str(epub_path))
        
        invalid_cfi = "invalid_cfi_format"
        valid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        
        with pytest.raises(CFIError):
            processor.extract_text_from_cfi_range(invalid_cfi, valid_cfi)
        
        processor.close()
    
    def test_context_manager(self):
        """Test using CFIProcessor as a context manager."""
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        
        with CFIProcessor(str(epub_path)) as processor:
            # Test that processor is functional within context
            result = processor.extract_text_from_cfi_range(
                "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)",
                "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:3)"
            )
            assert result == "xxx"
        
        # Context manager should have closed resources
        # (We don't test internal state as that's implementation-specific)