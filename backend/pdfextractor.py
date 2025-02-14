""" The PDF Exractor Module """

from io import BytesIO

import requests
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from fastapi import HTTPException


class PDFExtractor:

    def __init__(self):

        self.la_params = LAParams(
            line_margin=0.5,
            word_margin=0.1,
            char_margin=2.0,
            detect_vertical=True
        )

    def extract_from_url(self, pdf_url: str) -> str:
        """
        Method that uses the requests library and PDF miner to extract text from the PDF URL

        Params:
        - pdf_url: Direct url to the pdf
        """

        try:
            # Stream the PDF content
            response = requests.get(pdf_url, stream=True)
            response.raise_for_status()

            # Create in-memory buffers for input and output
            pdf_buffer = BytesIO(response.content)
            text_buffer = BytesIO()

            # Extract text directly from memory to memory
            extract_text_to_fp(pdf_buffer, text_buffer,
                               laparams=self.la_params)

            # Get the extracted text
            text = text_buffer.getvalue().decode('utf-8')

            # Clean up
            pdf_buffer.close()
            text_buffer.close()

            return text

        except requests.RequestException as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to download PDF: {str(e)}"
            ) from e
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Failed to decode PDF text. File might be corrupted or encoded incorrectly."
            ) from e
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error while processing PDF: {str(e)}"
            ) from e
