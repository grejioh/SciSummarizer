# src/pdf_processor.py

import PyPDF2
import logging
from typing import Optional

class PDFProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def extract_text(self, pdf_path: str) -> Optional[str]:
        """
        Extract text from a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
        
        Returns:
            Optional[str]: Extracted text from the PDF, or None if extraction failed.
        """
        try:
            self.logger.info(f"Extracting text from PDF: {pdf_path}")
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            self.logger.info(f"Successfully extracted {len(text)} characters from {pdf_path}")
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            return None

    def extract_text_from_page(self, pdf_path: str, page_number: int) -> Optional[str]:
        """
        Extract text from a specific page of a PDF file.
        
        Args:
            pdf_path (str): Path to the PDF file.
            page_number (int): Page number to extract (0-indexed).
        
        Returns:
            Optional[str]: Extracted text from the specified page, or None if extraction failed.
        """
        try:
            self.logger.info(f"Extracting text from page {page_number} of PDF: {pdf_path}")
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                if page_number >= len(reader.pages):
                    raise ValueError(f"Page number {page_number} out of range")
                
                text = reader.pages[page_number].extract_text()
            
            self.logger.info(f"Successfully extracted {len(text)} characters from page {page_number} of {pdf_path}")
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text from page {page_number} of {pdf_path}: {str(e)}")
            return None

    def extract_text_from_fisrt_N_pages(self, pdf_path: str, max_pages_num: int) -> Optional[str]:
        try:
            text = ""
            for page_number in range(max_pages_num):
                page_text = self.extract_text_from_page(pdf_path, page_number)
                if page_text:
                    text += page_text + "\n"
                else:
                    break  # 如果某一页的文本提取失败，停止提取
            self.logger.info(f"Successfully extracted {len(text)} characters from the first {max_pages_num} pages of {pdf_path}")
            return text.strip()
        except Exception as e:
            self.logger.error(f"Error extracting text from first {page_number} pages of {pdf_path}: {str(e)}")
            return None
            

# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    processor = PDFProcessor()
    
    pdf_path = "data/pdfs/Optimal_Stochastic_Resource_Allocation_for_Distrib.pdf"
    full_text = processor.extract_text(pdf_path)
    if full_text:
        print(f"Extracted text (first 100 characters): {full_text[:100]}...")
    
    page_text = processor.extract_text_from_page(pdf_path, 0)  # Extract text from the first page
    if page_text:
        print(f"Extracted text from first page (first 100 characters): {page_text[:100]}...")
