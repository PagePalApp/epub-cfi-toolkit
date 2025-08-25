"""
Tests for CFIParser class.
Tests CFI parsing functionality and specification compliance.
"""

import pytest

from epub_cfi_toolkit import CFIError
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


class TestBasicCFIParsing:
    """Test basic CFI parsing functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
    def test_simple_cfi_parsing(self):
        """Test parsing a simple CFI."""
        cfi = "epubcfi(/6/4!/4/2/1:5)"
        parsed = self.parser.parse(cfi)
        
        # Check spine steps
        assert len(parsed.spine_steps) == 2
        assert parsed.spine_steps[0].index == 6
        assert parsed.spine_steps[1].index == 4
        
        # Check content steps
        assert len(parsed.content_steps) == 3
        assert parsed.content_steps[0].index == 4
        assert parsed.content_steps[1].index == 2
        assert parsed.content_steps[2].index == 1
        
        # Check location
        assert parsed.location.offset == 5
        assert parsed.location.length is None
    
    def test_cfi_with_assertions(self):
        """Test CFI parsing with element assertions."""
        cfi = "epubcfi(/6/4[chap01ref]!/4[body01]/2[para01]/1:0)"
        parsed = self.parser.parse(cfi)
        
        assert parsed.spine_steps[1].assertion == "chap01ref"
        assert parsed.content_steps[0].assertion == "body01"
        assert parsed.content_steps[1].assertion == "para01"
        assert parsed.content_steps[2].assertion is None
    
    def test_location_range_syntax(self):
        """Test location with range syntax (:offset~length)."""
        cfi = "epubcfi(/6/4!/4/2/1:5~10)"
        parsed = self.parser.parse(cfi)
        
        assert parsed.location.offset == 5
        assert parsed.location.length == 10


class TestCFIComparison:
    """Test CFI comparison functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
    def test_same_position_comparison(self):
        """Test comparison of identical CFIs."""
        cfi1 = self.parser.parse("epubcfi(/6/4!/4/2/1:5)")
        cfi2 = self.parser.parse("epubcfi(/6/4!/4/2/1:5)")
        
        assert self.parser.compare_cfis(cfi1, cfi2) == 0
    
    def test_different_offset_comparison(self):
        """Test comparison of CFIs with different offsets."""
        cfi1 = self.parser.parse("epubcfi(/6/4!/4/2/1:5)")
        cfi2 = self.parser.parse("epubcfi(/6/4!/4/2/1:10)")
        
        assert self.parser.compare_cfis(cfi1, cfi2) == -1
        assert self.parser.compare_cfis(cfi2, cfi1) == 1
    
    def test_different_spine_comparison(self):
        """Test comparison of CFIs in different spine items."""
        cfi1 = self.parser.parse("epubcfi(/6/4!/4/2/1:5)")
        cfi2 = self.parser.parse("epubcfi(/6/6!/4/2/1:5)")
        
        assert self.parser.compare_cfis(cfi1, cfi2) == -1
        assert self.parser.compare_cfis(cfi2, cfi1) == 1


class TestStepIndexSemantics:
    """Test even/odd step index semantics per specification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
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


class TestEdgeCasesAndErrorConditions:
    """Test edge cases and error conditions from the specification."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = CFIParser()
    
    def test_empty_cfi(self):
        """Test empty CFI raises appropriate error."""
        with pytest.raises(CFIError, match="CFI cannot be empty"):
            self.parser.parse("")
    
    def test_whitespace_only_cfi(self):
        """Test CFI with only whitespace raises appropriate error."""
        with pytest.raises(CFIError, match="CFI must start with"):
            self.parser.parse("   ")
    
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
        
        # spine_assertion should return None for insufficient spine steps
        assert parsed.spine_assertion is None