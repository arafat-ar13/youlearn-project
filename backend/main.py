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
    allow_origins=["http://localhost:3000", "https://youlearn-project-site.vercel.app", "https://purple-stone-0a77e4410.4.azurestaticapps.net"],
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

def fix_url(url: str) -> str:
    """
    Fix URL if it has a single slash after protocol
    This is needed specifically for Azure App Service
    """
    # Check for the common Azure issue with https:/ instead of https://
    if url.startswith("https:/") and not url.startswith("https://"):
        fixed_url = "https://" + url[7:]
        print(f"Fixed URL from {url} to {fixed_url}")
        return fixed_url
    
    # Check for the same issue with http:/
    if url.startswith("http:/") and not url.startswith("http://"):
        fixed_url = "http://" + url[6:]
        print(f"Fixed URL from {url} to {fixed_url}")
        return fixed_url
        
    return url

@app.get("/proxy-pdf/{url:path}")
async def proxy_pdf(url: str):
    """
    Proxy endpoint to serve PDFs with proper CORS headers
    """
    try:
        # Fix URL if needed
        url = fix_url(url)
        
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
        # Fix URL if needed
        url = fix_url(url)
        
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
