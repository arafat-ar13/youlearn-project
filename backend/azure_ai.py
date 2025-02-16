import os
from io import BytesIO
from typing import Optional

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (AnalyzeDocumentRequest,
                                                  AnalyzeResult)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()

client = DocumentIntelligenceClient(
    endpoint=os.getenv("AZURE_ENDPOINT"),
    credential=AzureKeyCredential(os.getenv("AZURE_KEY"))
)


def get_text_from_pdf(url: str, page_num: Optional[int] = None) -> str:
    """
    Extract text from a PDF using Azure Document Intelligence API.
    Can extract from a specific page or the entire document.

    Args:
        url: URL of the PDF document
        page_num: Optional page number (0-based) to extract from. If None, processes entire document.

    Returns:
        Extracted text as string
    """
    poller = client.begin_analyze_document(
        "prebuilt-read",
        AnalyzeDocumentRequest(url_source=url)
    )
    result: AnalyzeResult = poller.result()

    if page_num is None:
        # Return text from entire document
        return result.content

    # Extract text from specific page
    page_text = ""

    # Azure's pages are 1-based, but we receive 0-based page numbers
    target_page = page_num + 1

    for page in result.pages:
        if page.pageNumber == target_page:
            # Process lines in reading order
            for line in page.lines:
                page_text += line.content + " "
            break

    return page_text.strip()


def get_page_count(url: str) -> int:
    """
    Get the total number of pages in a PDF document

    Args:
        url: URL of the PDF document

    Returns:
        Total number of pages
    """
    poller = client.begin_analyze_document(
        "prebuilt-read",
        AnalyzeDocumentRequest(url_source=url)
    )
    result: AnalyzeResult = poller.result()
    return len(result.pages)


def get_text_with_bboxes(pdf_buffer: BytesIO, page_num: Optional[int] = None) -> dict:
    """
    Extract text and bounding boxes from a PDF using Azure Document Intelligence API.

    Args:
        url: URL of the PDF document
        page_num: Optional page number (0-based) to extract from. If None, processes entire document.

    Returns:
        Dictionary containing text content and bounding box information
    """
    poller = client.begin_analyze_document(
        "prebuilt-read",
        AnalyzeDocumentRequest(bytes_source=pdf_buffer.getvalue())
    )
    result: AnalyzeResult = poller.result()

    blocks = []
    text = ""

    if page_num is not None:
        # Skip pages we're not interested in if page_num is specified
        page = result.pages[0]

        page_text = ""
        for line in page.lines:
            page_text += line.content + " "

            # Add bounding box information
            # Azure returns polygon as [x1, y1, x2, y2, x3, y3, x4, y4]
            polygon = line.polygon
            if polygon and len(polygon) >= 8:
                # Extract coordinates
                x_coords = [polygon[i] for i in range(0, len(polygon), 2)]
                y_coords = [polygon[i] for i in range(1, len(polygon), 2)]

                # Convert to x0,y0,x1,y1 format (min/max coordinates)
                bbox = [
                    min(x_coords),  # x0
                    min(y_coords),  # y0
                    max(x_coords),  # x1
                    max(y_coords)   # y1
                ]

                blocks.append({
                    "text": line.content,
                    "page": page.page_number - 1,  # Convert to 0-based
                    "bbox": bbox
                })

        text += page_text.strip() + "\n\n"

    return {
        "text": text.strip(),
        "blocks": blocks
    }
