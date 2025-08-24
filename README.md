# EPUB CFI Toolkit

A Python toolkit for processing EPUB Canonical Fragment Identifiers (CFIs). This library provides functionality to identify text in EPUB files using CFIs, convert between text locations and CFIs, and validate CFI strings.

## Features

- **CFI Validation**: Validate EPUB CFI strings for correct syntax
- **Text to CFI**: Convert text locations within EPUB files to CFI strings
- **CFI to Text**: Extract text content from EPUB files using CFI references
- **EPUB Processing**: Handle EPUB file structure and navigation

## Installation

```bash
pip install epub-cfi-toolkit
```

## Quick Start

```python
from epub_cfi_toolkit import CFIProcessor, CFIValidator

# Validate a CFI string
validator = CFIValidator()
is_valid = validator.validate("/6/4[chap01ref]!/4[body01]/10[para05]/3:10")

# Process EPUB file with CFI
processor = CFIProcessor("path/to/your/book.epub")
text = processor.extract_text_from_cfi("/6/4[chap01ref]!/4[body01]/10[para05]/3:10")
```

## Requirements

- Python 3.8+
- lxml

## Development

```bash
# Clone the repository
git clone https://github.com/PagePalApp/epub-cfi-toolkit.git
cd epub-cfi-toolkit

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Format code
black epub_cfi_toolkit tests
isort epub_cfi_toolkit tests

# Type checking
mypy epub_cfi_toolkit
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.