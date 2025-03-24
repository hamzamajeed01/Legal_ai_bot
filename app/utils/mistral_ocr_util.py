import os
import logging
from pathlib import Path
from mistralai import Mistral, DocumentURLChunk
import PyPDF2

# Get logger for this module
logger = logging.getLogger("mistral_ocr")

# Initialize Mistral client
mistral_client = Mistral(api_key=os.getenv('MISTRAL_API_KEY'))

def process_pdf_with_mistral_ocr(pdf_file_path):
    """
    Process a PDF file using Mistral OCR API
    
    Args:
        pdf_file_path: Path to the PDF file
        
    Returns:
        Extracted text in markdown format
    """
    logger.info(f"Processing PDF with Mistral OCR: {os.path.basename(pdf_file_path)}")
    
    try:
        # Read file
        with open(pdf_file_path, "rb") as f:
            file_bytes = f.read()
            file_size = len(file_bytes) / 1024  # Size in KB
            logger.info(f"File size: {file_size:.2f} KB")
        
        # Upload file to Mistral
        logger.info("Uploading file to Mistral")
        uploaded_file = mistral_client.files.upload(
            file={
                "file_name": os.path.basename(pdf_file_path),
                "content": file_bytes,
            },
            purpose="ocr"
        )
        logger.info(f"File uploaded successfully with ID: {uploaded_file.id}")
        
        # Get signed URL
        logger.info("Getting signed URL")
        signed_url = mistral_client.files.get_signed_url(file_id=uploaded_file.id, expiry=1)
        
        # Process with OCR
        logger.info("Processing with OCR")
        ocr_response = mistral_client.ocr.process(
            document=DocumentURLChunk(document_url=signed_url.url),
            model="mistral-ocr-latest"
        )
        
        # Extract markdown from all pages
        page_count = len(ocr_response.pages)
        logger.info(f"OCR processing completed. Document has {page_count} pages")
        
        markdowns = []
        for page_idx, page in enumerate(ocr_response.pages, 1):
            logger.debug(f"Extracting markdown from page {page_idx}/{page_count}")
            markdowns.append(page.markdown)
        
        combined_markdown = "\n\n".join(markdowns)
        logger.info(f"Successfully extracted {len(combined_markdown)} characters of text")
        
        return combined_markdown
    except Exception as e:
        logger.error(f"Error in Mistral OCR processing: {str(e)}", exc_info=True)
        raise Exception(f"Mistral OCR API error: {str(e)}")

def extract_text_with_pypdf(pdf_file_path):
    """
    Fallback method to extract text using PyPDF2
    
    Args:
        pdf_file_path: Path to the PDF file
        
    Returns:
        Extracted text
    """
    logger.info(f"Extracting text with PyPDF2: {os.path.basename(pdf_file_path)}")
    
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file_path)
        page_count = len(pdf_reader.pages)
        logger.info(f"PDF has {page_count} pages")
        
        text = ""
        for page_idx, page in enumerate(pdf_reader.pages, 1):
            logger.debug(f"Extracting text from page {page_idx}/{page_count}")
            page_text = page.extract_text()
            text += page_text + "\n"
        
        logger.info(f"Successfully extracted {len(text)} characters of text")
        return text
    except Exception as e:
        logger.error(f"Error extracting text with PyPDF2: {str(e)}", exc_info=True)
        raise Exception(f"Error extracting text with PyPDF2: {str(e)}") 