# Code Style Guide

This document outlines the code style standards for the EPUB CFI Toolkit project. All contributors must follow these guidelines to maintain consistency and quality across the codebase.

> **Note:** This document focuses on detailed code style specifications. For general contribution guidelines, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Table of Contents

- [Overview](#overview)
- [Python Code Formatting](#python-code-formatting)
- [Import Organization](#import-organization)
- [Linting Standards](#linting-standards)
- [Type Hints](#type-hints)
- [Naming Conventions](#naming-conventions)
- [Documentation Standards](#documentation-standards)
- [Development Tools](#development-tools)
- [IDE Configuration](#ide-configuration)
- [Enforcement](#enforcement)

## Overview

The project uses automated tools to enforce consistent code style:

- **Black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting and style checking
- **mypy** - Type checking

All code must pass these checks before being merged.

## Python Code Formatting

### Line Length
- **Maximum line length: 95 characters** (configured in `.flake8`)
- **Black formatting: 88 characters** (configured in `pyproject.toml`)
- flake8 allows up to 95 characters to accommodate cases where Black's 88-character formatting still produces lines slightly over 88 characters
- Long lines should be broken using Black's automatic formatting

### String Quotes
- Use **double quotes** for strings (Black default)
- Use single quotes only when the string contains double quotes

```python
# Good
message = "Hello, world!"
sql_query = 'SELECT * FROM table WHERE name = "John"'

# Avoid
message = 'Hello, world!'
```

### Trailing Commas
- Use trailing commas in multi-line collections (Black handles this automatically)

```python
# Good
items = [
    "first",
    "second",
    "third",
]
```

## Import Organization

### Import Order (isort)
The project uses isort with the "black" profile for import sorting:

1. Standard library imports
2. Third-party imports
3. Local application imports

```python
# Standard library
import re
from pathlib import Path
from typing import List, Optional

# Third-party
from lxml import etree

# Local application
from .exceptions import CFIError
from .cfi_parser import CFIParser
```

### Import Style
- Use absolute imports for modules within the package
- Use relative imports only for closely related modules
- Avoid wildcard imports (`from module import *`)

```python
# Good
from epub_cfi_toolkit import CFIProcessor
from .exceptions import CFIError

# Avoid
from epub_cfi_toolkit import *
```

## Linting Standards

### flake8 Configuration
The project uses flake8 with the following configuration (`.flake8`):

```ini
[flake8]
max-line-length = 95
extend-ignore = E203,W503
```

### Ignored Errors
- **E203**: Whitespace before ':' (conflicts with Black)
- **W503**: Line break before binary operator (conflicts with Black)

### Required Checks
All code must pass flake8's critical checks:
- **E9**: Runtime errors (syntax errors, undefined names)
- **F63**: Invalid comparisons
- **F7**: Syntax errors in doctests
- **F82**: Undefined names

## Type Hints

### Required Type Hints
- All public functions and methods must have type hints
- Class attributes should be type hinted when their type is not obvious
- Use `Optional[T]` for nullable parameters

### Type Hint Style
```python
from typing import List, Optional

def extract_text_from_cfi_range(
    self, start_cfi: str, end_cfi: str
) -> str:
    """Extract text content between two CFI positions."""
    pass

def process_items(items: List[str]) -> Optional[str]:
    """Process a list of items and return result."""
    pass
```

### mypy Configuration
The project uses mypy with the following settings:

```toml
[tool.mypy]
python_version = "3.9"
warn_return_any = false
warn_unused_configs = true
disallow_untyped_defs = false
check_untyped_defs = true
```

## Naming Conventions

### Variables and Functions
- Use `snake_case` for variables and functions
- Use descriptive names that clearly indicate purpose
- Avoid single-letter variables except for short loops

```python
# Good
cfi_processor = CFIProcessor(epub_path)
extracted_text = processor.extract_text_from_cfi_range(start, end)

# Avoid
p = CFIProcessor(epub_path)
t = processor.extract_text_from_cfi_range(start, end)
```

### Classes
- Use `PascalCase` for class names
- Use descriptive names that indicate the class purpose

```python
# Good
class CFIProcessor:
class ManifestItem:

# Avoid
class cfiProcessor:
class item:
```

### Constants
- Use `UPPER_SNAKE_CASE` for module-level constants
- Group related constants together

```python
# Good
DEFAULT_ENCODING = "utf-8"
MAX_CFI_LENGTH = 1000

# Avoid
default_encoding = "utf-8"
MaxCfiLength = 1000
```

### Private Members
- Use single leading underscore for internal use
- Use double leading underscore for name mangling (rare)

```python
class CFIParser:
    def __init__(self):
        self._step_pattern = re.compile(r"/(\d+)")  # Internal use
        
    def _parse_steps(self, path: str):  # Internal method
        pass
```

## Documentation Standards

### Docstring Format
Use Google-style docstrings for all public functions and classes:

```python
def extract_text_from_cfi_range(
    self, start_cfi: str, end_cfi: str
) -> str:
    """
    Extract text content between two CFI positions.
    
    Args:
        start_cfi: The CFI string marking the start of the range
        end_cfi: The CFI string marking the end of the range
        
    Returns:
        The extracted text content between the two positions
        
    Raises:
        CFIError: If the CFIs are invalid or text cannot be extracted
    """
```

### Code Comments
- Use comments sparingly to explain "why", not "what"
- Prefer clear code over comments when possible
- Use TODO comments for temporary workarounds

```python
# Good
# CFI uses 1-based indexing, convert to 0-based for Python
array_index = (cfi_index // 2) - 1

# Avoid
# Set array_index to cfi_index divided by 2 minus 1
array_index = (cfi_index // 2) - 1
```

## Development Tools

### Required Tools
Install all development tools with:

```bash
pip install -e .[dev]
```

This includes:
- `black>=22.0` - Code formatting
- `isort>=5.0` - Import sorting  
- `flake8>=4.0` - Linting
- `mypy>=1.0` - Type checking
- `pytest>=7.0` - Testing
- `lxml-stubs>=0.4.0` - Type stubs for lxml

### Running Tools

```bash
# Format code
black epub_cfi_toolkit/

# Sort imports
isort epub_cfi_toolkit/

# Check linting
flake8 epub_cfi_toolkit/

# Type checking
mypy epub_cfi_toolkit/

# Run all checks
black epub_cfi_toolkit/ && isort epub_cfi_toolkit/ && flake8 epub_cfi_toolkit/ && mypy epub_cfi_toolkit/
```

## IDE Configuration

### Visual Studio Code
Create `.vscode/settings.json`:

```json
{
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length=88"],
    "python.sortImports.args": ["--profile=black"],
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.enabled": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

### PyCharm
1. Install the Black plugin
2. Configure Black as the default formatter
3. Enable flake8 and mypy inspections
4. Set line length to 88 in Black settings

## Enforcement

### Pre-commit Hooks (Recommended)
Set up pre-commit hooks to automatically check code style:

```bash
pip install pre-commit
```

Create `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8
```

### CI/CD Enforcement
All pull requests must pass the following checks in GitHub Actions:

1. **Syntax Check**: `flake8 --select=E9,F63,F7,F82`
2. **Style Check**: `flake8` with full configuration
3. **Type Check**: `mypy epub_cfi_toolkit`
4. **Test Coverage**: Tests must maintain >90% coverage

### Manual Verification
Before submitting a PR, run:

```bash
# Quick style check
flake8 epub_cfi_toolkit/
mypy epub_cfi_toolkit/
pytest tests/

# Full formatting (if needed)
black epub_cfi_toolkit/
isort epub_cfi_toolkit/
```

## Summary

Following these code style guidelines ensures:

- **Consistency** across all project files
- **Readability** for all contributors
- **Maintainability** over time
- **Quality** through automated checking
- **Compatibility** with CI/CD pipelines

All code must pass Black, isort, flake8, and mypy checks before being merged to maintain these standards.