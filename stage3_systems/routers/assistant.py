from fastapi import APIRouter
from pydantic import BaseModel, Field

from stage4_rag.retriever import Retriever

router = APIRouter(prefix="/assistant", tags=["Assistant"])

# Load the document index once when this module is imported.
retriever = Retriever()


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1, max_length=1000)


@router.post("/ask")
def ask_assistant(request: QuestionRequest):
    results = retriever.search(request.question, top_k=3)

    if not results:
        return {
            "success": True,
            "answer": (
                "I couldn't find relevant information in the "
                "available company documents. Please contact "
                "the appropriate team."
            ),
            "sources": []
        }

    sources = [
        {
            "source": result["source"],
            "text": result["text"]
        }
        for result in results
    ]

    return {
        "success": True,
        "answer": (
            "I found these relevant passages in the company "
            "documents. Review the sources below to confirm "
            "they answer your question."
        ),
        "sources": sources
    }