from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests
from pydantic import BaseModel
from pdfextractor import PDFExtractor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextBlock(BaseModel):
    text: str
    page: int
    bbox: List[float]
    width: float
    height: float
    method: str

class PDFResponse(BaseModel):
    text: str
    blocks: List[TextBlock]

@app.get("/proxy-pdf/{url:path}")
async def proxy_pdf(url: str):
    """
    Proxy endpoint to serve PDFs with proper CORS headers
    """
    try:
        print(f"Attempting to fetch PDF from: {url}")  # Debug logging
        
        
        response = requests.get(
            url, 
            stream=True,
        )        
        # Log response details
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        response.raise_for_status()
        
        return StreamingResponse(
            response.iter_content(chunk_size=8192),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=document.pdf",
                "Content-Type": "application/pdf",
                "Access-Control-Allow-Origin": "http://localhost:3000"
            }
        )
    except requests.RequestException as e:
        print(f"Request error: {str(e)}")  # Debug logging
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch PDF: {str(e)}"
        )
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  # Debug logging
        raise HTTPException(
            status_code=500, 
            detail=f"Unexpected error: {str(e)}"
        )

@app.get("/extract/{url:path}", response_model=PDFResponse)
async def extract(url: str):
    """
    Extract text from a PDF URL
    """
    try:
        extractor = PDFExtractor()
        result = extractor.extract(url)
        
        return PDFResponse(
            text=result["text"],
            blocks=result["blocks"]
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) from e