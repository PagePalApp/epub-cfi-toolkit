"""
Tests for the CFI processor.
"""

import pytest
from unittest.mock import Mock, patch
from pathlib import Path

from epub_cfi_toolkit import CFIProcessor, EPUBError, CFIError


class TestCFIProcessor:
    """Test cases for the CFIProcessor class."""
    
    def test_init_nonexistent_file(self):
        """Test initialization with non-existent EPUB file."""
        with pytest.raises(EPUBError, match="EPUB file not found"):
            CFIProcessor("nonexistent.epub")
    
    @patch('epub_cfi_toolkit.cfi_processor.zipfile.ZipFile')
    @patch('epub_cfi_toolkit.cfi_processor.Path.exists')
    def test_init_valid_epub(self, mock_exists, mock_zipfile):
        """Test initialization with valid EPUB file."""
        mock_exists.return_value = True
        mock_zip = Mock()
        mock_zipfile.return_value = mock_zip
        mock_zip.read.return_value = b'''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        
        processor = CFIProcessor("test.epub")
        assert processor._opf_path == "content.opf"
        processor.close()
    
    @patch('epub_cfi_toolkit.cfi_processor.zipfile.ZipFile')
    @patch('epub_cfi_toolkit.cfi_processor.Path.exists')
    def test_extract_text_from_cfi_not_implemented(self, mock_exists, mock_zipfile):
        """Test that extract_text_from_cfi raises NotImplementedError."""
        mock_exists.return_value = True
        mock_zip = Mock()
        mock_zipfile.return_value = mock_zip
        mock_zip.read.return_value = b'''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        
        processor = CFIProcessor("test.epub")
        
        with pytest.raises(NotImplementedError):
            processor.extract_text_from_cfi("/2/4[chap01ref]")
        
        processor.close()
    
    @patch('epub_cfi_toolkit.cfi_processor.zipfile.ZipFile')
    @patch('epub_cfi_toolkit.cfi_processor.Path.exists')
    def test_create_cfi_from_location_not_implemented(self, mock_exists, mock_zipfile):
        """Test that create_cfi_from_location raises NotImplementedError."""
        mock_exists.return_value = True
        mock_zip = Mock()
        mock_zipfile.return_value = mock_zip
        mock_zip.read.return_value = b'''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        
        processor = CFIProcessor("test.epub")
        
        with pytest.raises(NotImplementedError):
            processor.create_cfi_from_location("chap01", "/html/body/p", 10)
        
        processor.close()
    
    @patch('epub_cfi_toolkit.cfi_processor.zipfile.ZipFile')
    @patch('epub_cfi_toolkit.cfi_processor.Path.exists')
    def test_context_manager(self, mock_exists, mock_zipfile):
        """Test using CFIProcessor as a context manager."""
        mock_exists.return_value = True
        mock_zip = Mock()
        mock_zipfile.return_value = mock_zip
        mock_zip.read.return_value = b'''<?xml version="1.0"?>
        <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
            <rootfiles>
                <rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>
            </rootfiles>
        </container>'''
        
        with CFIProcessor("test.epub") as processor:
            assert processor._epub_zip is not None
        
        # After exiting context, zip should be closed
        mock_zip.close.assert_called_once()