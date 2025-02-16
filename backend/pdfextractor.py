from io import BytesIO

import fitz
import requests
from fastapi import HTTPException

from azure_ai import get_text_with_bboxes


class PDFExtractor:
    def __init__(self):
        pass

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

    def _get_page_buffer(self, page) -> BytesIO:
        """
        Convert a single page to a PDF buffer

        Args:
            page: fitz.Page object

        Returns:
            BytesIO buffer containing single-page PDF
        """
        # Create a new PDF document with just this page
        doc_single = fitz.open()
        doc_single.insert_pdf(
            page.parent, from_page=page.number, to_page=page.number)

        # Get the bytes and create a buffer
        pdf_bytes = doc_single.write()
        page_buffer = BytesIO(pdf_bytes)

        # Clean up
        doc_single.close()

        return page_buffer

    def _process_page(self, pdf_buffer, page, page_num: int) -> tuple:
        """
        Process a single page using PyMuPDF, falling back to Azure AI if needed

        Args:
            page: fitz.Page object
            page_num: Page number (0-based)
            pdf_url: Original PDF URL for Azure AI fallback

        Returns:
            Tuple of (display_text, blocks) where blocks contain text and bbox info
        """
        page_blocks = page.get_text("blocks")
        page_text = ""
        blocks = []

        # Check if page has searchable text
        has_text = any(block[4].strip() for block in page_blocks)

        # print(has_text)?

        if has_text:
            print("PyMUUUU")
            # Process searchable text with PyMuPDF
            for block in page_blocks:
                text = block[4].strip()
                if text:
                    page_text += text + "\n\n"
                    blocks.append({
                        "text": text,
                        "page": page_num,
                        "bbox": list(block[0:4])  # x0,y0,x1,y1
                    })
        else:
            # Use Azure AI for non-searchable page
            print(f"AZURE:")

            # page_buffer = self._get_page_buffer(page)

            azure_result = get_text_with_bboxes(pdf_buffer, page_num=page_num)
            if azure_result["text"]:
                page_text = azure_result["text"]
                blocks.extend(azure_result["blocks"])

        return page_text, blocks

    def extract_with_pymu(self, pdf_url: str) -> dict:
        """
        Extract text from PDF using PyMuPDF with fallback to Azure AI for non-searchable pages

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
                page_text, page_blocks = self._process_page(pdf_buffer, page, page_num)

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
