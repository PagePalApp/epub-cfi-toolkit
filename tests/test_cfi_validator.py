"""
Tests for the CFI validator.
"""

import pytest

from epub_cfi_toolkit import CFIValidator, CFIValidationError


class TestCFIValidator:
    """Test cases for the CFIValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = CFIValidator()
    
    def test_valid_cfis(self):
        """Test validation of valid CFI strings."""
        valid_cfis = [
            "/2",
            "/2/4",
            "/2/4[chap01ref]",
            "/2/4[chap01ref]!/4[body01]/10[para05]",
            "/2/4[chap01ref]!/4[body01]/10[para05]/3:10",
            "/6/4[chap01ref]!/4[body01]/10[para05]/3:10~5",
        ]
        
        for cfi in valid_cfis:
            assert self.validator.validate(cfi), f"CFI should be valid: {cfi}"
    
    def test_invalid_cfis(self):
        """Test validation of invalid CFI strings."""
        invalid_cfis = [
            "",
            "2",  # Missing leading slash
            "/",  # Just a slash
            "/a",  # Non-numeric step
            "2/4",  # Missing leading slash
            "/2/",  # Trailing slash with no step
            "/2//4",  # Double slash
        ]
        
        for cfi in invalid_cfis:
            assert not self.validator.validate(cfi), f"CFI should be invalid: {cfi}"
    
    def test_validate_strict_valid(self):
        """Test strict validation with valid CFI."""
        valid_cfi = "/2/4[chap01ref]!/4[body01]/10[para05]/3:10"
        # Should not raise an exception
        self.validator.validate_strict(valid_cfi)
    
    def test_validate_strict_invalid(self):
        """Test strict validation with invalid CFI."""
        invalid_cfi = "invalid_cfi"
        with pytest.raises(CFIValidationError):
            self.validator.validate_strict(invalid_cfi)
    
    def test_validate_non_string(self):
        """Test validation with non-string input."""
        assert not self.validator.validate(None)
        assert not self.validator.validate(123)
        assert not self.validator.validate([])
    
    def test_validate_empty_string(self):
        """Test validation with empty string."""
        assert not self.validator.validate("")