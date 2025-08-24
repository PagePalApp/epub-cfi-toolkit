**Disclaimer**: everything in this repository was generated entirely by Claude Code (including this README) and has not been reviewed or verified by a human. Content may be inaccurate or incomplete. Use at your own risk.

# EPUB CFI Toolkit

[![PyPI version](https://badge.fury.io/py/epub-cfi-toolkit.svg)](https://badge.fury.io/py/epub-cfi-toolkit)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/PagePalApp/epub-cfi-toolkit/workflows/CI/badge.svg)](https://github.com/PagePalApp/epub-cfi-toolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python toolkit for extracting text from EPUB files using **Canonical Fragment Identifiers (CFIs)** with enhanced validation.

## Installation

```bash
pip install epub-cfi-toolkit
```

## Quick Start

```python
from epub_cfi_toolkit import CFIProcessor, CFIValidator

# Extract text between two CFI positions
with CFIProcessor("book.epub") as processor:
    text = processor.extract_text_from_cfi_range(
        start_cfi="epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)",
        end_cfi="epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:20)"
    )
    print(text)  # "This is the extracted text"

# Validate CFI syntax
validator = CFIValidator()
is_valid = validator.validate("epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)")

# Validate CFI against document structure (enhanced)
with CFIProcessor("book.epub") as processor:
    if processor.validate_cfi_bounds("epubcfi(/6/4!/4/2/1:0)"):
        # CFI references valid elements
        text = processor.extract_text_from_cfi_range(start_cfi, end_cfi)
    else:
        print("CFI references non-existent elements")
```

## Features

- **Text Extraction**: Extract text between CFI positions with character precision
- **Enhanced Validation**: Validate CFIs against actual document structure
- **Helpful Error Messages**: Clear errors with element context and valid ranges
- **Cross-Element Support**: Handle text extraction across XML elements
- **Type Safety**: Full type hints for better development experience

## API Reference

### CFIProcessor

```python
class CFIProcessor:
    def extract_text_from_cfi_range(self, start_cfi: str, end_cfi: str) -> str:
        """Extract text between two CFI positions."""
    
    def validate_cfi_bounds(self, cfi: str) -> bool:
        """Check if CFI references valid elements."""
    
    def validate_cfi_bounds_strict(self, cfi: str) -> None:
        """Validate CFI bounds with detailed error messages."""
```

### CFIValidator

```python
class CFIValidator:
    def validate(self, cfi: str) -> bool:
        """Validate CFI syntax."""
    
    def validate_strict(self, cfi: str) -> None:
        """Validate CFI syntax, raise CFIValidationError if invalid."""
```

## Enhanced Validation

Get helpful error messages for invalid CFI references:

```python
from epub_cfi_toolkit import CFIProcessor, CFIError

try:
    with CFIProcessor("book.epub") as processor:
        processor.validate_cfi_bounds_strict("epubcfi(/6/50!/4/2/1:0)")
except CFIError as e:
    print(e)
    # "CFI references spine item 50 but document only has 3 spine items (valid range: 2-6)"
```

## Error Handling

```python
from epub_cfi_toolkit import CFIProcessor, CFIError, EPUBError

try:
    with CFIProcessor("book.epub") as processor:
        text = processor.extract_text_from_cfi_range(start_cfi, end_cfi)
except EPUBError as e:
    print(f"EPUB file error: {e}")
except CFIError as e:
    print(f"CFI error: {e}")
```

## What are EPUB CFIs?

EPUB Canonical Fragment Identifiers are a standard way to reference specific locations within EPUB documents.

**Example**: `epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)`

- `/6` - Spine reference
- `/4[chap01ref]` - Chapter reference  
- `!` - Content separator
- `/4[body01]/10[para05]` - Navigate to paragraph
- `/3:10` - Character offset 10 in text node 3

## Development

```bash
git clone https://github.com/PagePalApp/epub-cfi-toolkit.git
cd epub-cfi-toolkit
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .[dev]
pytest
```

## License

MIT License - see [LICENSE](LICENSE) file for details.