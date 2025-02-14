import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import (AnalyzeDocumentRequest,
                                                  AnalyzeResult)
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

load_dotenv()


client = DocumentIntelligenceClient(
    endpoint=os.getenv("AZURE_ENDPOINT"), credential=AzureKeyCredential(os.getenv("AZURE_KEY"))
)

def get_text_from_pdf(url: str) -> str:
    poller = client.begin_analyze_document(
        "prebuilt-read", AnalyzeDocumentRequest(url_source=url
                                                ))
    result: AnalyzeResult = poller.result()

    return result.content
