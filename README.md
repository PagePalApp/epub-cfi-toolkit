**Disclaimer**: everything in this repository was generated entirely by Claude Code (including this README) and has not been reviewed or verified by a human. Content may be inaccurate or incomplete. Use at your own risk.

# EPUB CFI Toolkit

[![PyPI version](https://badge.fury.io/py/epub-cfi-toolkit.svg)](https://badge.fury.io/py/epub-cfi-toolkit)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI](https://github.com/PagePalApp/epub-cfi-toolkit/workflows/CI/badge.svg)](https://github.com/PagePalApp/epub-cfi-toolkit/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A Python toolkit for processing **EPUB Canonical Fragment Identifiers (CFIs)**. This library provides functionality to extract text from EPUB files using CFI references and navigate EPUB document structure.

## 🚀 Quick Start

### Installation

```bash
pip install epub-cfi-toolkit
```

### Basic Usage

```python
from epub_cfi_toolkit import CFIProcessor

# Simple usage - extract text from an EPUB file using CFI range
processor = CFIProcessor("path/to/book.epub")
text = processor.extract_text_from_cfi_range(
    start_cfi="epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)",
    end_cfi="epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:20)"
)
print(text)  # "This is the extracted text from the EPUB"

```

## 📚 Features

- **✅ CFI Range Text Extraction**: Extract text between two CFI positions with character-level precision
- **✅ Cross-Element Support**: Handle text extraction across different XML elements
- **✅ EPUB Structure Parsing**: Navigate EPUB spine, manifest, and content documents
- **✅ Error Handling**: Comprehensive error handling with descriptive messages
- **✅ Type Safety**: Full type hints for better development experience

## 🎯 Use Cases

### Simple Text Extraction
```python
from epub_cfi_toolkit import CFIProcessor

# Direct usage for simple text extraction
processor = CFIProcessor("frankenstein.epub")
text = processor.extract_text_from_cfi_range(
    "epubcfi(/6/6!/4/2/10/1:0)",     # Start CFI
    "epubcfi(/6/6!/4/2/10/3:150)"    # End CFI  
)
print(text)  # Extracted text from the novel
```

### Extract Text from EPUB Annotations
```python
from epub_cfi_toolkit import CFIProcessor

# Extract highlighted text or notes from EPUB files
processor = CFIProcessor("novel.epub")
# Extract a specific paragraph
paragraph = processor.extract_text_from_cfi_range(
    "epubcfi(/6/14!/4/2/4/1:0)",    # Start of paragraph  
    "epubcfi(/6/14!/4/2/4/1:150)"   # First 150 characters
)
print(f"Extracted: {paragraph}")
```


### Batch Process Multiple EPUBs
```python
from epub_cfi_toolkit import CFIProcessor
import os

def extract_from_multiple_books(epub_folder, cfi_start, cfi_end):
    results = []
    
    for epub_file in os.listdir(epub_folder):
        if epub_file.endswith('.epub'):
            epub_path = os.path.join(epub_folder, epub_file)
            
            try:
                processor = CFIProcessor(epub_path)
                text = processor.extract_text_from_cfi_range(cfi_start, cfi_end)
                results.append((epub_file, text.strip()))
            except Exception as e:
                print(f"Error processing {epub_file}: {e}")
    
    return results

# Extract the same CFI range from multiple books
results = extract_from_multiple_books(
    "books/", 
    "epubcfi(/6/6!/4/2/22/1:0)", 
    "epubcfi(/6/6!/4/2/22/3:15)"
)
```

## 📖 API Reference

### CFIProcessor

The main class for processing EPUB files and extracting text using CFIs.

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

## 🧪 Advanced Examples

### Working with Complex CFI Paths
```python
from epub_cfi_toolkit import CFIProcessor

# CFIs can reference complex document structures
processor = CFIProcessor("textbook.epub")
# Extract from nested elements
citation = processor.extract_text_from_cfi_range(
    "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/2/1:0)",  # Inside <em> tag
    "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/2/1:25)"  # First 25 chars
)

# Extract across multiple elements  
full_paragraph = processor.extract_text_from_cfi_range(
    "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/1:0)",    # Start of paragraph
    "epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:100)"   # Including tail text
)
```

### Error Handling Best Practices
```python
from epub_cfi_toolkit import CFIProcessor, CFIError, EPUBError

def safe_extract_text(epub_path, start_cfi, end_cfi):
    try:
        processor = CFIProcessor(epub_path)
        return processor.extract_text_from_cfi_range(start_cfi, end_cfi)
            
    except EPUBError as e:
        print(f"EPUB file error: {e}")
        return None
        
    except CFIError as e:
        print(f"CFI processing error: {e}")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Safe extraction with error handling
result = safe_extract_text("book.epub", "epubcfi(/6/4!/4/2/1:0)", "epubcfi(/6/4!/4/2/1:50)")
if result:
    print(f"Extracted: {result}")
```

## 🛠️ Requirements

- **Python 3.8+** (tested on 3.8, 3.9, 3.10, 3.11, 3.12)
- **lxml** - XML processing library

## 🏗️ Development

```bash
# Clone the repository
git clone https://github.com/PagePalApp/epub-cfi-toolkit.git
cd epub-cfi-toolkit

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:  
source venv/bin/activate

# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=epub_cfi_toolkit --cov-report=html

# Code formatting
black epub_cfi_toolkit tests
isort epub_cfi_toolkit tests

# Type checking
mypy epub_cfi_toolkit

# Linting
flake8 epub_cfi_toolkit
```

## 📋 What are EPUB CFIs?

EPUB Canonical Fragment Identifiers (CFIs) are a standard way to reference specific locations within EPUB documents. They work like precise bookmarks that can point to:

- Specific characters within text
- Elements within the document structure  
- Ranges of text across multiple elements

**Example CFI**: `epubcfi(/6/4[chap01ref]!/4[body01]/10[para05]/3:10)`

This CFI breaks down as:
- `/6` - Reference to spine item
- `/4[chap01ref]` - Chapter 1 reference  
- `!` - Separator (spine reference / content reference)
- `/4[body01]/10[para05]` - Navigate to paragraph 5 in body
- `/3:10` - Character offset 10 in the 3rd text node

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`pytest`)
6. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
7. Push to the branch (`git push origin feature/AmazingFeature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built according to the [EPUB CFI specification](https://idpf.org/epub/linking/cfi/)
- Developed with ❤️ for the EPUB and digital publishing community
- Part of the [PagePal](https://github.com/PagePalApp) ecosystem