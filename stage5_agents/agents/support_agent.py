from stage4_rag.retriever import Retriever


class SupportAgent:
    def __init__(self):
        self.retriever = Retriever()

    def run(self, question):
        if not question or not question.strip():
            return {
                "success": False,
                "agent": "Support Agent",
                "message": "Please enter a question."
            }

        results = self.retriever.search(question, top_k=3)

        if not results:
            return {
                "success": True,
                "agent": "Support Agent",
                "message": (
                    "I could not find relevant information in the "
                    "available company documents. Please check with "
                    "the appropriate team."
                ),
                "sources": []
            }

        passages = [
            {
                "source": result["source"],
                "text": result["text"],
                "score": result["score"]
            }
            for result in results
        ]

        return {
            "success": True,
            "agent": "Support Agent",
            "message": (
                "I found these relevant passages. Please check "
                "the source text to confirm it answers your question."
            ),
            "sources": passages
        }