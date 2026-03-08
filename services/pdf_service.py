from pypdf import PdfReader
from pypdf.errors import PdfReadError
from io import BytesIO
import logging

logger = logging.getLogger(__name__)

class PDFService:
    """Service for extracting text from PDF documents"""
    
    @staticmethod
    async def extract_text(file_bytes: bytes) -> str:
        """
        Extract text from PDF file bytes.
        
        Args:
            file_bytes: Raw PDF file content
            
        Returns:
            Extracted text from all pages concatenated
            
        Raises:
            Exception: If PDF is corrupted or unreadable
        """
        try:
            reader = PdfReader(BytesIO(file_bytes))
            text = ""
            
            # Extract text from all pages
            for page_num, page in enumerate(reader.pages):
                try:
                    page_text = PDFService._extract_page_text(page)
                    if page_text:
                        text += page_text + "\n\n"
                except Exception as page_error:
                    logger.warning(f"Failed to extract text from page {page_num + 1}: {page_error}")
                    continue
            
            # Check if any text was extracted
            if not text.strip():
                logger.warning("No text could be extracted from PDF")
                raise Exception("No text could be extracted from this PDF. It may be an image-based PDF.")
            
            logger.info(f"Successfully extracted {len(text)} characters from PDF")
            return text.strip()
            
        except PdfReadError as e:
            logger.error(f"Invalid or corrupted PDF: {e}")
            raise Exception("This file appears to be corrupted or is not a valid PDF.")
        except Exception as e:
            if "No text could be extracted" in str(e):
                raise
            logger.error(f"PDF processing error: {e}")
            raise Exception("Failed to process PDF. Please try a different file.")
    
    @staticmethod
    def _extract_page_text(page) -> str:
        """
        Extract text from a single PDF page, handling errors gracefully.
        
        Args:
            page: pypdf page object
            
        Returns:
            Extracted text from the page
        """
        try:
            text = page.extract_text()
            return text if text else ""
        except Exception as e:
            logger.warning(f"Error extracting text from page: {e}")
            return ""
