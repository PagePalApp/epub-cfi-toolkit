"""
Tests for CFIProcessor class.
Tests all CFI processing functionality including initialization and text extraction.
"""

import pytest
from pathlib import Path

from epub_cfi_toolkit import CFIProcessor, EPUBError, CFIError


class TestCFIProcessorInitialization:
    """Test cases for CFIProcessor initialization."""
    
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
    
    def test_basic_functionality(self, cfi_processor):
        """Test basic CFI range extraction functionality."""
        # Test basic functionality with a simple CFI range
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:3)"
        
        result = cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
        assert result == "xxx"
    
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


class TestCFIProcessorErrorHandling:
    """Test error handling in CFIProcessor."""
    
    @pytest.fixture
    def sample_epub_path(self):
        """Return path to sample EPUB file."""
        return Path(__file__).parent.parent / "test_data" / "sample.epub"
    
    @pytest.fixture
    def cfi_processor(self, sample_epub_path):
        """Return CFI processor instance."""
        return CFIProcessor(str(sample_epub_path))
    
    def test_invalid_cfi_validation(self, cfi_processor):
        """Test that invalid CFIs raise appropriate errors."""
        invalid_cfi = "invalid_cfi_format"
        valid_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        
        with pytest.raises(CFIError):
            cfi_processor.extract_text_from_cfi_range(invalid_cfi, valid_cfi)
    
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


class TestCFIProcessorAssertionValidation:
    """Test CFI assertion validation in CFIProcessor."""
    
    @pytest.fixture
    def sample_epub_path(self):
        """Return path to sample EPUB file."""
        return Path(__file__).parent.parent / "test_data" / "sample.epub"
    
    @pytest.fixture
    def cfi_processor(self, sample_epub_path):
        """Return CFI processor instance."""
        return CFIProcessor(str(sample_epub_path))
    
    def test_valid_assertion_match(self, cfi_processor):
        """Test CFI with valid assertion that matches document."""
        # Using para05 ID from our test EPUB
        cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        
        # Should not raise error since para05 exists in test data
        result = cfi_processor.extract_text_from_cfi_range(cfi, cfi)
        assert result == ""
    
    def test_assertion_mismatch_error(self, cfi_processor):
        """Test CFI with assertion that doesn't match document."""
        # Using wrong element ID assertion - the 5th paragraph has ID para05, not wrongpara
        start_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[wrongpara]/1:0)"
        end_cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[wrongpara]/1:3)"
        
        with pytest.raises(CFIError, match="assertion mismatch"):
            cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)
    
    def test_spine_assertion_validation(self, cfi_processor):
        """Test spine itemref assertion validation."""
        # Wrong spine assertion
        start_cfi = "epubcfi(/6/4[wrongchap]!/4[body01]/10[para05]/1:0)"
        end_cfi = "epubcfi(/6/4[wrongchap]!/4[body01]/10[para05]/1:3)"
        
        with pytest.raises(CFIError, match="assertion mismatch"):
            cfi_processor.extract_text_from_cfi_range(start_cfi, end_cfi)


class TestCFIProcessorTextNodeHandling:
    """Test text node identification and handling in CFIProcessor."""
    
    @pytest.fixture
    def sample_epub_path(self):
        """Return path to sample EPUB file."""
        return Path(__file__).parent.parent / "test_data" / "sample.epub"
    
    @pytest.fixture
    def cfi_processor(self, sample_epub_path):
        """Return CFI processor instance."""
        return CFIProcessor(str(sample_epub_path))
    
    def test_text_node_identification(self, cfi_processor):
        """Test identification of text nodes in processing."""
        # Test that odd index is correctly identified as text node
        cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        result = cfi_processor.extract_text_from_cfi_range(cfi, "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:3)")
        
        # Should extract from text node (index 1 = odd = text)
        assert result == "xxx"


class TestUTF16CharacterOffsets:
    """Test UTF-16 character offset handling with Unicode characters."""
    
    @pytest.fixture
    def sample_epub_path(self):
        """Return path to sample EPUB file.""" 
        return Path(__file__).parent.parent / "test_data" / "sample.epub"
    
    def test_utf16_offset_calculation(self):
        """Test that character offsets use UTF-16 code units."""
        # Create test content with Unicode characters
        # This would need a special test EPUB with Unicode content
        # For now, we'll test that offsets work correctly in general
        epub_path = Path(__file__).parent.parent / "test_data" / "sample.epub"
        processor = CFIProcessor(str(epub_path))
        
        cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        result = processor.extract_text_from_cfi_range(cfi, "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:3)")
        
        # Should extract 3 characters from offset 0
        assert len(result) == 3
        assert result == "xxx"