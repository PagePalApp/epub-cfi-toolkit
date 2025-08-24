"""
EPUB file structure parsing functionality.
"""

import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass

from lxml import etree

from .exceptions import EPUBError


@dataclass
class ManifestItem:
    """Represents an item in the EPUB manifest."""
    id: str
    href: str
    media_type: str
    properties: Optional[str] = None


@dataclass
class SpineItem:
    """Represents an item in the EPUB spine."""
    id: str
    idref: str
    linear: bool = True


class EPUBParser:
    """Parser for EPUB file structure and metadata."""
    
    def __init__(self, epub_path: str):
        """
        Initialize EPUB parser.
        
        Args:
            epub_path: Path to the EPUB file
            
        Raises:
            EPUBError: If EPUB cannot be opened or parsed
        """
        self.epub_path = Path(epub_path)
        self._epub_zip: Optional[zipfile.ZipFile] = None
        self._opf_path: Optional[str] = None
        self._manifest: Dict[str, ManifestItem] = {}
        self._spine: List[SpineItem] = []
        
        if not self.epub_path.exists():
            raise EPUBError(f"EPUB file not found: {epub_path}")
        
        try:
            self._epub_zip = zipfile.ZipFile(self.epub_path, 'r')
            self._parse_container()
            self._parse_opf()
        except Exception as e:
            if self._epub_zip:
                self._epub_zip.close()
            raise EPUBError(f"Failed to parse EPUB: {e}")
    
    def _parse_container(self) -> None:
        """Parse META-INF/container.xml to find OPF file."""
        try:
            if self._epub_zip is None:
                raise EPUBError("EPUB file not properly initialized")
            container_data = self._epub_zip.read("META-INF/container.xml")
            container_xml = etree.fromstring(container_data)
            
            # Find the OPF file path
            rootfile = container_xml.find(
                ".//{urn:oasis:names:tc:opendocument:xmlns:container}rootfile"
            )
            if rootfile is not None:
                self._opf_path = rootfile.get("full-path")
            else:
                raise EPUBError("Could not find OPF file in container.xml")
        except Exception as e:
            raise EPUBError(f"Failed to parse container.xml: {e}")
    
    def _parse_opf(self) -> None:
        """Parse the OPF file to extract manifest and spine."""
        if not self._opf_path:
            raise EPUBError("OPF path not found")
        
        try:
            if self._epub_zip is None:
                raise EPUBError("EPUB file not properly initialized")
            if self._opf_path is None:
                raise EPUBError("OPF path not found")
            opf_data = self._epub_zip.read(self._opf_path)
            opf_xml = etree.fromstring(opf_data)
            
            # Define namespace
            ns = {'opf': 'http://www.idpf.org/2007/opf'}
            
            # Parse manifest
            manifest = opf_xml.find('.//opf:manifest', ns)
            if manifest is not None:
                for item in manifest.findall('opf:item', ns):
                    manifest_item = ManifestItem(
                        id=item.get('id'),
                        href=item.get('href'),
                        media_type=item.get('media-type'),
                        properties=item.get('properties')
                    )
                    self._manifest[manifest_item.id] = manifest_item
            
            # Parse spine
            spine = opf_xml.find('.//opf:spine', ns)
            if spine is not None:
                for i, itemref in enumerate(spine.findall('opf:itemref', ns)):
                    spine_item = SpineItem(
                        id=itemref.get('id', f'spine_item_{i}'),
                        idref=itemref.get('idref'),
                        linear=itemref.get('linear', 'yes') == 'yes'
                    )
                    self._spine.append(spine_item)
                    
        except Exception as e:
            raise EPUBError(f"Failed to parse OPF file: {e}")
    
    @property
    def manifest(self) -> Dict[str, ManifestItem]:
        """Get the manifest items."""
        return self._manifest.copy()
    
    @property
    def spine(self) -> List[SpineItem]:
        """Get the spine items."""
        return self._spine.copy()
    
    def get_spine_item_by_index(self, index: int) -> Optional[SpineItem]:
        """
        Get spine item by 1-based index (CFI uses 1-based indexing).
        
        Args:
            index: 1-based spine index
            
        Returns:
            SpineItem if found, None otherwise
        """
        # CFI uses 1-based indexing, but spine index in CFI is actually:
        # /2 = first spine item, /4 = second spine item, etc.
        # So we need to convert: CFI_index = (spine_array_index + 1) * 2
        spine_array_index = (index // 2) - 1
        
        if 0 <= spine_array_index < len(self._spine):
            return self._spine[spine_array_index]
        return None
    
    def get_content_document_path(self, spine_item: SpineItem) -> str:
        """
        Get the full path to a content document within the EPUB.
        
        Args:
            spine_item: The spine item to get path for
            
        Returns:
            Full path to the content document
            
        Raises:
            EPUBError: If manifest item not found
        """
        manifest_item = self._manifest.get(spine_item.idref)
        if not manifest_item:
            raise EPUBError(f"Manifest item not found: {spine_item.idref}")
        
        # Combine OPF directory with href
        if self._opf_path is None:
            raise EPUBError("OPF path not found")
        opf_dir = str(Path(self._opf_path).parent)
        if opf_dir == '.':
            return manifest_item.href
        else:
            return f"{opf_dir}/{manifest_item.href}"
    
    def read_content_document(self, spine_item: SpineItem) -> bytes:
        """
        Read the content of a document from the EPUB.
        
        Args:
            spine_item: The spine item to read
            
        Returns:
            Raw document content as bytes
            
        Raises:
            EPUBError: If document cannot be read
        """
        document_path = self.get_content_document_path(spine_item)
        
        try:
            if self._epub_zip is None:
                raise EPUBError("EPUB file not properly initialized")
            return self._epub_zip.read(document_path)
        except Exception as e:
            raise EPUBError(f"Failed to read document {document_path}: {e}")
    
    def close(self) -> None:
        """Close the EPUB file."""
        if self._epub_zip:
            self._epub_zip.close()
            self._epub_zip = None
    
    def __enter__(self) -> 'EPUBParser':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self.close()