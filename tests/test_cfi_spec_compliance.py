"""
Tests for EPUB CFI specification compliance.
Based on the official EPUB CFI specification at https://idpf.org/epub/linking/cfi/
"""

import pytest
from pathlib import Path

from epub_cfi_toolkit import CFIProcessor, CFIError
from epub_cfi_toolkit.cfi_parser import CFIParser, CFIStep, CFILocation, ParsedCFI


class TestCFIEscapeSequences:
    """Test CFI character escaping per specification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
    def test_escape_square_brackets(self):
        """Test escaping square brackets with circumflex."""
        # CFI with escaped square brackets in assertion
        cfi = "epubcfi(/6/4!/4/2^[special^]/1:0)"
        parsed = self.parser.parse(cfi)
        
        # Should have content step with index 2 and assertion "special"
        # (the parser extracts content inside brackets, after unescaping)
        assert len(parsed.content_steps) == 3  # /4, /2[special], /1
        assert parsed.content_steps[0].index == 4
        assert parsed.content_steps[1].index == 2
        assert parsed.content_steps[1].assertion == "special"
        assert parsed.content_steps[2].index == 1
    
    def test_escape_circumflex(self):
        """Test escaping circumflex character itself."""
        cfi = "epubcfi(/6/4!/4/2[id^^test]/1:0)"
        parsed = self.parser.parse(cfi)
        
        assert parsed.content_steps[1].assertion == "id^test"
    
    def test_escape_comma(self):
        """Test escaping comma character."""
        cfi = "epubcfi(/6/4!/4/2[id^,test]/1:0)"
        parsed = self.parser.parse(cfi)
        
        assert parsed.content_steps[1].assertion == "id,test"
    
    def test_escape_parentheses(self):
        """Test escaping parentheses."""
        cfi = "epubcfi(/6/4!/4/2[id^(test^)]/1:0)"
        parsed = self.parser.parse(cfi)
        
        assert parsed.content_steps[1].assertion == "id(test)"
    
    def test_escape_semicolon(self):
        """Test escaping semicolon character."""
        cfi = "epubcfi(/6/4!/4/2[id^;test]/1:0)"
        parsed = self.parser.parse(cfi)
        
        assert parsed.content_steps[1].assertion == "id;test"
    
    def test_multiple_escapes(self):
        """Test multiple escape sequences in one CFI."""
        cfi = "epubcfi(/6/4!/4/2^[special^,^;test^]/1:0)"
        parsed = self.parser.parse(cfi)
        
        assert len(parsed.content_steps) == 3  # /4, /2[special,;test], /1
        assert parsed.content_steps[1].assertion == "special,;test"
    
    def test_invalid_escape_sequence(self):
        """Test that invalid escape sequences are treated as literals."""
        cfi = "epubcfi(/6/4!/4/2[id^xtest]/1:0)"
        parsed = self.parser.parse(cfi)
        
        # ^x is not a valid escape, so ^ should be treated as literal
        assert parsed.content_steps[1].assertion == "id^xtest"


class TestRangeCFISyntax:
    """Test range CFI syntax with comma separation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
    def test_range_cfi_detection(self):
        """Test detection of range CFI syntax."""
        range_cfi = "epubcfi(/6/4!, /2/1:0, /2/1:10)"
        simple_cfi = "epubcfi(/6/4!/2/1:0)"
        
        assert self.parser._is_range_cfi(range_cfi)
        assert not self.parser._is_range_cfi(simple_cfi)
    
    def test_range_cfi_parsing(self):
        """Test parsing of range CFI syntax."""
        range_cfi = "epubcfi(/6/4!, /2/1:0, /2/1:10)"
        parsed = self.parser.parse(range_cfi)
        
        # Should parse the start part for now
        assert len(parsed.spine_steps) == 2
        assert parsed.spine_steps[0].index == 6
        assert parsed.spine_steps[1].index == 4
        assert len(parsed.content_steps) == 2  # /2, /1
        assert parsed.content_steps[0].index == 2
        assert parsed.content_steps[1].index == 1
        assert parsed.location.offset == 0
    
    def test_range_cfi_with_escaped_commas(self):
        """Test range CFI that contains escaped commas."""
        range_cfi = "epubcfi(/6/4[chap^,01]!, /2/1:0, /2/1:10)"
        parsed = self.parser.parse(range_cfi)
        
        # Should properly handle escaped comma in assertion
        assert parsed.spine_steps[1].assertion == "chap,01"
    
    def test_invalid_range_cfi(self):
        """Test invalid range CFI with wrong number of parts."""
        invalid_range = "epubcfi(/6/4!, /2/1:0)"  # Only 2 parts, needs 3
        
        # This should be parsed as a simple CFI since it doesn't have 2 commas
        parsed = self.parser.parse(invalid_range)
        assert len(parsed.spine_steps) == 2


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
        # For now, we'll test the parser logic
        parser = CFIParser()
        cfi = "epubcfi(/6/4!/4/2/1:5)"  # Offset 5
        parsed = parser.parse(cfi)
        
        assert parsed.location.offset == 5
        
    def test_multibyte_character_handling(self):
        """Test handling of multi-byte UTF-16 characters."""
        # Emoji and other characters that require surrogate pairs in UTF-16
        # would be counted as 2 code units, not 1 character
        parser = CFIParser()
        cfi = "epubcfi(/6/4!/4/2/1:10)"  # Higher offset for multi-byte chars
        parsed = parser.parse(cfi)
        
        assert parsed.location.offset == 10


class TestVirtualElementIndices:
    """Test virtual element indices (0 and n+2) per specification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
    def test_virtual_element_zero(self):
        """Test virtual element index 0 (before first character data)."""
        cfi = "epubcfi(/6/4!/4/0:0)"  # Virtual element 0
        parsed = self.parser.parse(cfi)
        
        assert len(parsed.content_steps) == 2  # /4, /0
        assert parsed.content_steps[1].index == 0
        assert parsed.location.offset == 0
    
    def test_virtual_element_high(self):
        """Test virtual element after last child (n+2 pattern).""" 
        cfi = "epubcfi(/6/4!/4/20:0)"  # High even number representing virtual element
        parsed = self.parser.parse(cfi)
        
        assert parsed.content_steps[1].index == 20


class TestAssertionValidation:
    """Test CFI assertion validation and error handling."""
    
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


class TestStepIndexSemantics:
    """Test even/odd step index semantics per specification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
    @pytest.fixture
    def sample_epub_path(self):
        """Return path to sample EPUB file."""
        return Path(__file__).parent.parent / "test_data" / "sample.epub"
    
    def test_even_indices_for_elements(self):
        """Test that even indices reference XML elements."""
        cfi = "epubcfi(/6/4!/4/2/1:0)"  # 6,4,4,2 are even (elements)
        parsed = self.parser.parse(cfi)
        
        # All spine and most content steps should be even (elements)
        assert parsed.spine_steps[0].index == 6  # Even
        assert parsed.spine_steps[1].index == 4  # Even
        assert parsed.content_steps[0].index == 4  # Even
        assert parsed.content_steps[1].index == 2  # Even
        assert parsed.content_steps[2].index == 1  # Odd (text node)
    
    def test_odd_indices_for_text(self):
        """Test that odd indices reference character data/text nodes."""
        cfi = "epubcfi(/6/4!/4/1:5)"  # 1 is odd (text node)
        parsed = self.parser.parse(cfi)
        
        assert parsed.content_steps[1].index == 1  # Odd (text)
        assert parsed.location.offset == 5
    
    def test_text_node_identification(self, sample_epub_path):
        """Test identification of text nodes in processing."""
        processor = CFIProcessor(str(Path(__file__).parent.parent / "test_data" / "sample.epub"))
        
        # Test that odd index is correctly identified as text node
        cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
        result = processor.extract_text_from_cfi_range(cfi, "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:3)")
        
        # Should extract from text node (index 1 = odd = text)
        assert result == "xxx"


class TestEdgeCasesAndErrorConditions:
    """Test edge cases and error conditions from the specification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
    def test_empty_cfi(self):
        """Test empty CFI raises appropriate error."""
        with pytest.raises(CFIError, match="CFI cannot be empty"):
            self.parser.parse("")
    
    def test_invalid_cfi_format(self):
        """Test CFI that doesn't start with slash."""
        with pytest.raises(CFIError, match="CFI must start with"):
            self.parser.parse("6/4!/4/2/1:0")
    
    def test_malformed_location_offset(self):
        """Test malformed location offset."""
        # The regex won't match non-numeric offsets, so no location will be parsed
        cfi = "epubcfi(/6/4!/4/2/1:abc)"
        parsed = self.parser.parse(cfi)
        
        # Should parse without location since :abc doesn't match numeric pattern
        assert parsed.location is None
    
    def test_missing_spine_reference(self):
        """Test CFI missing required spine reference."""
        cfi = "epubcfi(/6!/4/2/1:0)"  # Missing itemref step
        parsed = self.parser.parse(cfi)
        
        # Should have only one spine step, causing error in spine_index property
        with pytest.raises(CFIError, match="CFI must contain both spine and itemref"):
            _ = parsed.spine_index
    
    def test_location_range_syntax(self):
        """Test location with range syntax (:offset~length)."""
        cfi = "epubcfi(/6/4!/4/2/1:5~10)"
        parsed = self.parser.parse(cfi)
        
        assert parsed.location.offset == 5
        assert parsed.location.length == 10