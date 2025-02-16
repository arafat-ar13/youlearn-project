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
        pdf_buffer: BytesIO buffer containing the PDF
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
        page = result.pages[0]
        current_paragraph = []
        last_y = None
        last_x = None

        for line in page.lines:
            current_y = line.polygon[1]  # Get y-coordinate of current line
            current_x = line.polygon[0]  # Get x-coordinate of current line
            
            # Check if this is potentially a new paragraph by looking at:
            # 1. Significant vertical gap
            # 2. Indentation at the start of a line
            # 3. Previous line ends with sentence-ending punctuation
            is_new_paragraph = False
            
            if last_y is not None:
                vertical_gap = current_y - last_y
                # Check for larger vertical gap indicating paragraph break
                if vertical_gap > 0.3:  # Adjusted threshold for paragraph separation
                    is_new_paragraph = True
                # Check for indentation
                elif last_x is not None and current_x - last_x > 0.3:
                    is_new_paragraph = True
                # Check if last line ended with sentence-ending punctuation
                elif current_paragraph and any(current_paragraph[-1].content.strip().endswith(p) 
                                            for p in ['.', '!', '?']):
                    # Only consider it a paragraph break if we're not in the middle of a sentence
                    next_word = line.content.strip()
                    if next_word and next_word[0].isupper():
                        is_new_paragraph = True

            if is_new_paragraph and current_paragraph:
                # Join current paragraph with single spaces and add double newline
                text += " ".join(l.content.strip() for l in current_paragraph) + "\n\n"
                current_paragraph = []

            current_paragraph.append(line)
            last_y = current_y
            last_x = current_x

            # Add bounding box information
            polygon = line.polygon
            if polygon and len(polygon) >= 8:
                x_coords = [polygon[i] for i in range(0, len(polygon), 2)]
                y_coords = [polygon[i] for i in range(1, len(polygon), 2)]

                bbox = [
                    min(x_coords),  # x0
                    min(y_coords),  # y0
                    max(x_coords),  # x1
                    max(y_coords)   # y1
                ]

                blocks.append({
                    "text": line.content,
                    "page": page_num,
                    "bbox": bbox
                })

        # Add the last paragraph if it exists
        if current_paragraph:
            text += " ".join(l.content.strip() for l in current_paragraph)

    return {
        "text": text.strip(),
        "blocks": blocks
    }