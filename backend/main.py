from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from pdfextractor import PDFExtractor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js app address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextBlock(BaseModel):
    text: str
    page: int
    bbox: List[float]

class PDFResponse(BaseModel):
    text: str
    blocks: List[TextBlock]

@app.get("/{name}")
async def root(name):
    return {"message": f"Hello {name}"}

@app.get("/extract/{url:path}", response_model=PDFResponse)
async def extract(url: str):
    """
    Extract text from a PDF URL
    """
    try:
        extractor = PDFExtractor()
        result = extractor.extract_with_pymu(url)
        
        # Since extract_with_pymu now returns a dict with 'text' and 'blocks'
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