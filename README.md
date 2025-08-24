**Disclaimer**: everything in this repository was generated entirely by Claude Code (including this README) and has not been reviewed or verified by a human. Content may be inaccurate or incomplete. Use at your own risk.

# EPUB CFI Toolkit

[![PyPI version](https://badge.fury.io/py/epub-cfi-toolkit.svg)](https://badge.fury.io/py/epub-cfi-toolkit)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/PagePalApp/epub-cfi-toolkit/workflows/CI/badge.svg)](https://github.com/PagePalApp/epub-cfi-toolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python toolkit for extracting text from EPUB files using **EPUB Canonical Fragment Identifiers (CFIs)** with full CFI specification compliance.

## Installation

```bash
pip install epub-cfi-toolkit
```

## Features

- **Full CFI Specification Compliance** - Supports all CFI features per EPUB CFI specification
- **Character Escaping** - Handles special characters with circumflex (^) escaping
- **Range CFI Support** - Processes both simple and range CFI syntax
- **Element Assertion Validation** - Validates element ID assertions in CFI paths
- **UTF-16 Character Offsets** - Proper Unicode handling for character positioning
- **Virtual Element Indices** - Support for virtual elements in DOM navigation

## Usage

### Basic Text Extraction

```python
from epub_cfi_toolkit import CFIProcessor

processor = CFIProcessor("path/to/book.epub")
text = processor.extract_text_from_cfi_range(
    start_cfi="epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)",
    end_cfi="epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:20)"
)
print(text)  # Extracted text from the EPUB
```

### CFI Parsing and Analysis

```python
from epub_cfi_toolkit import CFIParser

parser = CFIParser()
parsed_cfi = parser.parse("epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)")

print(parsed_cfi.spine_index)        # 4 (itemref index)
print(parsed_cfi.spine_assertion)    # "chap01ref" (element ID)
print(parsed_cfi.location.offset)    # 0 (character offset)
```

### Range CFI Processing

```python
# Range CFI with comma syntax
range_cfi = "epubcfi(/6/4[chapter]!, /2/1:5, /2/1:15)"
parsed = parser.parse(range_cfi)
```

### Character Escaping

CFIs automatically handle escaped special characters:

```python
# CFI with escaped characters: [, ], ^, ,, (, ), ;
cfi = "epubcfi(/6/4!/2[element^[with^]brackets]/1:0)"
parsed = parser.parse(cfi)  # Correctly handles escaped brackets
```

## API Reference

### CFIProcessor

```python
class CFIProcessor:
    def __init__(self, epub_path: str) -> None:
        """Initialize processor with EPUB file path."""
    
    def extract_text_from_cfi_range(self, start_cfi: str, end_cfi: str) -> str:
        """Extract text between two CFI positions with full spec compliance."""
```

### CFIParser

```python
class CFIParser:
    def __init__(self) -> None:
        """Initialize CFI parser with specification compliance."""
    
    def parse(self, cfi: str) -> ParsedCFI:
        """Parse CFI string with support for simple and range CFIs."""
    
    def compare_cfis(self, cfi1: ParsedCFI, cfi2: ParsedCFI) -> int:
        """Compare two CFIs for document order (-1, 0, 1)."""
```

### EPUBParser

```python
class EPUBParser:
    def __init__(self, epub_path: str) -> None:
        """Initialize parser for EPUB file structure."""
```

### Data Classes

```python
@dataclass
class CFIStep:
    index: int                    # Step index
    assertion: Optional[str]      # Element ID assertion

@dataclass  
class CFILocation:
    offset: int                   # Character offset
    length: Optional[int]         # Range length (optional)

@dataclass
class ParsedCFI:
    spine_steps: List[CFIStep]    # Spine navigation steps
    content_steps: List[CFIStep]  # Content navigation steps
    location: Optional[CFILocation] # Character position
```

### Exceptions

```python
from epub_cfi_toolkit import CFIError, EPUBError

# CFIError: Base exception for CFI parsing/processing errors
# EPUBError: Raised when EPUB file cannot be processed
```

## CFI Specification Compliance

This library fully implements the EPUB CFI specification including:

### Character Escaping
Special characters are escaped with circumflex (^): `[ ] ^ , ( ) ;`
```python
# Original: element[with]brackets  
# Escaped:  element^[with^]brackets
```

### Range CFI Syntax
Supports comma-separated range CFIs:
```python
# Format: epubcfi(parent_path, start_offset, end_offset)  
"epubcfi(/6/4[chapter]!, /2/1:5, /2/1:15)"
```

### Element Assertions
Validates element ID assertions in square brackets:
```python
"epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)"
#              ^^^^^^^^       ^^^^^^     ^^^^^^
#              Element ID assertions are validated
```

### Virtual Element Indices  
Handles virtual elements (indices 0 and beyond last child):
```python
"/4/0"    # Before first child element
"/4/10"   # After last child (if only 8 children exist)
```

## What are EPUB CFIs?

EPUB Canonical Fragment Identifiers (CFIs) are a standard way to reference specific locations within EPUB documents.

**CFI Structure**: `epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)`

- `epubcfi(...)` - CFI wrapper
- `/6` - Package document reference  
- `/4[chap01ref]` - Spine item reference with assertion
- `!` - Separator (spine / content boundary)
- `/4[body01]/10[para05]` - Content navigation path
- `/3:10` - Text node (3) with character offset (10)

## Requirements

- **Python 3.8+**
- **lxml** - XML/HTML processing library

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.