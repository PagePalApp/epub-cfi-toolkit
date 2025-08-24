**Disclaimer**: everything in this repository was generated entirely by Claude Code (including this README) and has not been reviewed or verified by a human. Content may be inaccurate or incomplete. Use at your own risk.

# EPUB CFI Toolkit

[![PyPI version](https://badge.fury.io/py/epub-cfi-toolkit.svg)](https://badge.fury.io/py/epub-cfi-toolkit)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/PagePalApp/epub-cfi-toolkit/workflows/CI/badge.svg)](https://github.com/PagePalApp/epub-cfi-toolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python toolkit for extracting text from EPUB files using **EPUB Canonical Fragment Identifiers (CFIs)**.

## Installation

```bash
pip install epub-cfi-toolkit
```

## Usage

```python
from epub_cfi_toolkit import CFIProcessor

processor = CFIProcessor("path/to/book.epub")
text = processor.extract_text_from_cfi_range(
    start_cfi="epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)",
    end_cfi="epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:20)"
)
print(text)  # Extracted text from the EPUB
```

## API

### CFIProcessor

```python
class CFIProcessor:
    def __init__(self, epub_path: str) -> None:
        """Initialize with path to EPUB file."""
    
    def extract_text_from_cfi_range(self, start_cfi: str, end_cfi: str) -> str:
        """Extract text between two CFI positions."""
```

### Exceptions

```python
from epub_cfi_toolkit import CFIError, EPUBError

# CFIError: Base exception for CFI-related errors
# EPUBError: Raised when EPUB file cannot be processed
```

## What are EPUB CFIs?

EPUB Canonical Fragment Identifiers (CFIs) are a standard way to reference specific locations within EPUB documents.

**Example CFI**: `epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)`

- `/6` - Reference to spine item
- `/4[chap01ref]` - Chapter reference  
- `!` - Separator (spine reference / content reference)
- `/4[body01]/10[para05]` - Navigate to paragraph 5 in body
- `/3:10` - Character offset 10 in the 3rd text node

## Requirements

- **Python 3.8+**
- **lxml** - XML processing library

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.