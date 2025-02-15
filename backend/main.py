from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pdfextractor import PDFExtractor

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js app address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PDFResponse(BaseModel):
    text: str


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
        pdf_text = extractor.extract_with_pymu(url)

        return PDFResponse(
            text=pdf_text
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) from e
