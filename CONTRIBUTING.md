# Contributing to EPUB CFI Toolkit

Thank you for your interest in contributing to the EPUB CFI Toolkit! This document provides guidelines and information for contributors.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Branching Strategy](#branching-strategy)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/epub-cfi-toolkit.git
   cd epub-cfi-toolkit
   ```
3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/PagePalApp/epub-cfi-toolkit.git
   ```

## Development Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies:**
   ```bash
   pip install -e .[dev]
   ```

3. **Verify the setup:**
   ```bash
   pytest tests/
   flake8 epub_cfi_toolkit/
   mypy epub_cfi_toolkit/
   ```

## Branching Strategy

We use a **GitHub Flow** branching strategy:

### Main Branch
- `main` - The stable production branch
- All releases are tagged from `main`
- Direct pushes to `main` are not allowed (except for maintainers)

### Feature Branches
- Create feature branches from `main`
- Use descriptive branch names with prefixes:
  - `feature/` - New features
  - `fix/` - Bug fixes  
  - `docs/` - Documentation changes
  - `refactor/` - Code refactoring
  - `test/` - Test improvements

**Examples:**
```bash
git checkout -b feature/add-cfi-validation
git checkout -b fix/handle-unicode-offsets
git checkout -b docs/api-reference
git checkout -b refactor/test-structure
```

### Branch Lifecycle
1. Create branch from latest `main`
2. Make changes and commit
3. Push branch to your fork
4. Open Pull Request to `main`
5. After review and CI passes, merge via GitHub
6. Delete the feature branch

## Commit Guidelines

We use **Conventional Commits** specification for all commit messages.

### Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### Types
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `style` - Code style changes (formatting, etc.)
- `refactor` - Code refactoring
- `test` - Adding or updating tests
- `chore` - Maintenance tasks, dependency updates
- `ci` - CI/CD pipeline changes

### Examples
```bash
feat: add support for range CFI syntax parsing
fix: handle escaped characters in CFI assertions
docs: add API reference for CFIProcessor class
refactor: reorganize test structure by class
test: add edge case tests for UTF-16 offsets
chore: update dependencies to latest versions
ci: add Python 3.12 to test matrix
```

### Commit Body Guidelines
- Use imperative mood ("Add feature" not "Added feature")
- Keep the first line under 72 characters
- Reference issues: "Fixes #123" or "Closes #456"
- Explain **what** and **why**, not **how**

## Pull Request Process

### Before Creating a PR

1. **Ensure your branch is up to date:**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run the full test suite locally:**
   ```bash
   pytest tests/
   flake8 epub_cfi_toolkit/
   mypy epub_cfi_toolkit/
   ```

3. **Check test coverage:**
   ```bash
   pytest tests/ --cov=epub_cfi_toolkit --cov-report=term-missing
   ```

### PR Title Format
Use the same **Conventional Commits** format for PR titles:
```
feat: add range CFI syntax support
fix: handle Unicode characters in text extraction  
docs: add contribution guidelines
```

### PR Description Template
```markdown
## Summary
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Test improvements

## Testing
- [ ] All existing tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated if needed
- [ ] No breaking changes (or documented)

Closes #issue_number
```

### Review Process
1. All PRs must pass CI checks
2. At least one maintainer review required
3. All conversations must be resolved
4. Branch must be up to date with `main`

## Code Standards

### Style Guidelines
- **Line Length:** Maximum 95 characters (configured in `.flake8`)
- **Formatting:** Use `black` for code formatting
- **Import Sorting:** Use `isort` for import organization
- **Linting:** Code must pass `flake8` checks
- **Type Hints:** Use type hints for all public APIs

### Code Quality
- Write clear, descriptive function and variable names
- Add docstrings for all public classes and methods
- Keep functions focused and small
- Avoid deep nesting (max 4 levels)
- Use meaningful exception messages

### Example Code Style
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

## Testing

### Test Organization
- `test_cfi_parser.py` - Tests for `CFIParser` class
- `test_cfi_processor.py` - Tests for `CFIProcessor` class
- Test files should mirror the structure of source files

### Writing Tests
- Use descriptive test names: `test_extract_single_character_from_cfi_range`
- Follow AAA pattern: Arrange, Act, Assert
- Test both positive and negative cases
- Use pytest fixtures for common setup

### Test Requirements
- **Coverage:** Maintain >90% test coverage
- **All Platforms:** Tests must pass on Python 3.8-3.12
- **Assertions:** Use informative assertion messages

### Running Tests
```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=epub_cfi_toolkit --cov-report=html

# Run specific test file
pytest tests/test_cfi_parser.py -v

# Run specific test
pytest tests/test_cfi_parser.py::TestBasicCFIParsing::test_simple_cfi_parsing -v
```

## Documentation

### Code Documentation
- All public APIs must have docstrings
- Use Google-style docstring format
- Include examples for complex functionality
- Document all parameters, return values, and exceptions

### README Updates
Update the README.md when adding:
- New features or functionality
- Installation requirements
- Usage examples
- Breaking changes

### Type Hints
- Use type hints for all function signatures
- Import types from `typing` module
- Use `Optional[T]` for nullable parameters
- Document complex types in docstrings

## CI/CD Pipeline

Our CI pipeline runs on every PR and includes:

1. **Linting:** `flake8` checks for code quality
2. **Type Checking:** `mypy` validates type hints
3. **Testing:** Full test suite on Python 3.8-3.12
4. **Coverage:** Test coverage reporting
5. **Build:** Package build verification

### CI Requirements
- All checks must pass (green status)
- Test coverage must not decrease
- No linting or type checking errors
- Package must build successfully

## Getting Help

- **Issues:** Use GitHub Issues for bug reports and feature requests
- **Discussions:** Use GitHub Discussions for questions and ideas
- **Documentation:** Check the README and inline documentation

## Code of Conduct

Please note that this project follows a standard Code of Conduct. Be respectful and constructive in all interactions.

---

Thank you for contributing to EPUB CFI Toolkit! 🎉