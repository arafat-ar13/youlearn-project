from io import BytesIO
import fitz
import requests
from fastapi import HTTPException

from google_ai import GoogleAIPDFExtractor

class PDFExtractor:
    def __init__(self):
        self.google_ai = GoogleAIPDFExtractor()
        
    def _check_url(self, pdf_url: str) -> requests.Response:
        """
        Validate URL and return PDF content buffer

        Args:
            pdf_url: Direct url to the pdf

        Returns:
            Response object containing the PDF content

        Raises:
            HTTPException: For various error conditions
        """
        try:
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

    def _process_page(self, page, page_num: int) -> tuple:
        """
        Process a single page using PyMuPDF, falling back to Google Cloud Vision for non-searchable pages

        Args:
            page: fitz.Page object
            page_num: Page number (0-based)

        Returns:
            Tuple of (display_text, blocks) where blocks contain text and bbox info
        """
        page_blocks = page.get_text("blocks")
        page_text = ""
        blocks = []

        # Check if page has searchable text
        has_text = any(block[4].strip() for block in page_blocks)

        if has_text:
            print(f"Page {page_num} processed with PyMuPDF")
            # Process searchable text with PyMuPDF
            for block in page_blocks:
                text = block[4].strip()
                if text:
                    page_text += text + "\n\n"
                    blocks.append({
                        "text": text,
                        "page": page_num,
                        "bbox": list(block[0:4]),  # x0,y0,x1,y1
                        "width": page.rect.width,
                        "height": page.rect.height,
                        "method": "pymupdf"
                    })
        else:
            print(f"Page {page_num} requires OCR, using Google Cloud Vision")
            # Use Google Cloud Vision for non-searchable page
            
            # Get page dimensions
            page_width = page.rect.width
            page_height = page.rect.height
            
            # Render the page to an image
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # Render at 300 DPI
            img_bytes = pix.tobytes(output="png")
            
            # Process with Google Vision
            google_result = self.google_ai.get_text_with_bboxes(
                img_bytes, page_num, page_width, page_height
            )
            
            if google_result["text"]:
                page_text = google_result["text"]
                blocks.extend(google_result["blocks"])

        return page_text, blocks

    def extract_with_pymu(self, pdf_url: str) -> dict:
        """
        Extract text from PDF using PyMuPDF with fallback to Google Cloud Vision for non-searchable pages

        Args:
            pdf_url: Direct url to the pdf

        Returns:
            Dictionary containing text content and bounding box information
        """
        try:
            response = self._check_url(pdf_url)
            pdf_buffer = BytesIO(response.content)
            doc = fitz.open(stream=pdf_buffer, filetype="pdf")

            result = {
                "text": "",  # Combined text for display
                "blocks": []  # List of {text, page, bbox} for highlighting
            }

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text, page_blocks = self._process_page(page, page_num)

                # Add page text and blocks to result
                result["text"] += page_text
                result["blocks"].extend(page_blocks)

                # Add page separator if not the last page
                if page_num < len(doc) - 1:
                    result["text"] += "\n\n---\n\n"

            # Clean up
            doc.close()
            pdf_buffer.close()

            # Clean up the display text
            result["text"] = result["text"].strip()
            result["text"] = result["text"].replace("\n\n\n", "\n\n")

            return result

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

    def extract(self, pdf_url: str) -> dict:
        """
        Top level extraction method that now uses extract_with_pymu
        """
        return self.extract_with_pymu(pdf_url)