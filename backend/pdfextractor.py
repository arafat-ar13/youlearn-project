""" The PDF Exractor Module """

from io import BytesIO

import requests
from fastapi import HTTPException
from pdfminer.converter import TextConverter
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFPageInterpreter, PDFResourceManager
from pdfminer.pdfpage import PDFPage

import fitz
import pymupdf

from azure_ai import get_text_from_pdf


class PDFExtractor:

    def __init__(self):

        self.la_params = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            detect_vertical=True
        )

    def _check_url(self, pdf_url: str) -> requests.Response:
        """
        Validate URL and return PDF content buffer

        Args:
            pdf_url: Direct url to the pdf

        Returns:
            Tuple containing the response and PDF buffer

        Raises:
            HTTPException: For various error conditions
        """
        try:
            # Stream the PDF content
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()

            return response

        except requests.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download PDF: {str(e)}"
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error while checking PDF URL: {str(e)}"
            ) from e

    def _extract_first_page(self, pdf_buffer: BytesIO) -> str:
        """
        Extract text from only the first page of the PDF

        Args:
            pdf_url: Direct url to the pdf

        Returns:
            Extracted text from the first page
        """
        try:
            # Get PDF content
            # _, pdf_buffer = self.check_url(pdf_url)

            # Create resource manager and output buffer
            resource_manager = PDFResourceManager()
            text_buffer = BytesIO()

            # Setup converter
            converter = TextConverter(
                resource_manager,
                text_buffer,
                laparams=self.la_params
            )

            # Setup interpreter
            interpreter = PDFPageInterpreter(resource_manager, converter)

            # Get pages (with maxpages=1 to only process first page)
            pages = PDFPage.get_pages(
                pdf_buffer,
                pagenos=[0],  # Zero-based index
                maxpages=1,
                caching=True
            )

            # Process only the first page
            for page in pages:
                interpreter.process_page(page)
                break  # Just in case, ensure we only process one page

            # Get text
            text = text_buffer.getvalue().decode('utf-8')

            # Clean up
            converter.close()
            text_buffer.close()
            # pdf_buffer.close()

            return text

        except UnicodeDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail="Failed to decode PDF text. File might be corrupted or encoded incorrectly."
            ) from e
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error while processing PDF: {str(e)}"
            ) from e
        
    def extract_with_pymu(self, pdf_url: str) -> str:
        """
        Extract text from PDF using PyMuPDF (fitz) with optimized performance.
        
        Args:
            pdf_url: Direct url to the pdf
            
        Returns:
            Formatted text from the PDF
        """
        try:
            # Get PDF content
            response = self._check_url(pdf_url)
            
            # Create a memory buffer from the response content
            pdf_buffer = BytesIO(response.content)
            
            # Open the PDF with PyMuPDF
            doc = fitz.open(stream=pdf_buffer, filetype="pdf")
            
            # Get text all at once with blocks formatting
            text = ""
            for page in doc:
                # Using "blocks" format maintains paragraph structure 
                # while being much faster than "dict" format
                page_text = page.get_text("blocks")
                
                # Join blocks with double newlines for paragraph separation
                if page_text:
                    text += "\n\n".join(block[4] for block in page_text if block[4].strip())
                    text += "\n\n---\n\n"  # Page separator
            
            # Clean up
            doc.close()
            pdf_buffer.close()
            
            # Basic cleanup of the text - single pass
            text = text.strip()
            text = text.replace("\n\n\n", "\n\n")  # Remove excessive newlines
            
            return text
                
        except fitz.FileDataError as e:
            raise HTTPException(
                status_code=400,
                detail="Invalid or corrupted PDF file"
            ) from e
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error while processing PDF: {str(e)}"
            ) from e
        
    def extract(self, pdf_url: str) -> str:
        """
        Top level extraction method. The function does the following:

        1) Checks the url for validity, and if valid:
        2) Creates a memory buffer out of the PDF file
        3) Extracts one page using PDF Miner to detect searchability.
        4) If searchable, extract text from the entire PDF using PDF Miner
        5) If not search, perform OCR, using:
            1) Azure Document Intelligence
            2) Tesserach (TODO)
        """
        try:
            response = self._check_url(pdf_url)

            # Create the buffer out of the PDF
            pdf_buffer = BytesIO(response.content)
            text_buffer = BytesIO()

            # # Extract first page
            first_page_text = self._extract_first_page(pdf_buffer)

            # Determine searchability
            if first_page_text != "\u000c":
                # If first page is not FF, extract the entire PDF next
                extract_text_to_fp(pdf_buffer, text_buffer,
                                   laparams=self.la_params)

                text = text_buffer.getvalue().decode("utf-8")

            else:
                # Use Azure AI
                text = get_text_from_pdf(pdf_url)

            # get_text_from_pdf(pdf_url)

            # Clean up
            pdf_buffer.close()
            text_buffer.close()

            return text

        except UnicodeDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail="Failed to decode PDF text. File might be corrupted or encoded incorrectly."
            ) from e
        except Exception as e:
            if isinstance(e, HTTPException):
                raise e
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error while processing PDF: {str(e)}"
            ) from e
