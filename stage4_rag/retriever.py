from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from stage4_rag.knowledge_base import load_knowledge_base


class Retriever:
    def __init__(self):
        self.passages = load_knowledge_base()

        if not self.passages:
            raise ValueError(
                "No knowledge-base passages found. "
                "Add a Markdown file to stage4_rag/documents/."
            )

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words="english",
            ngram_range=(1, 2)
        )

        passage_texts = [
            passage["text"] for passage in self.passages
        ]

        # Build the searchable representation of the documents.
        self.document_vectors = self.vectorizer.fit_transform(
            passage_texts
        )

    def search(self, question, top_k=3):
        """Return the most relevant passages for a question."""
        if not question or not question.strip():
            return []

        question_vector = self.vectorizer.transform([question])

        scores = cosine_similarity(
            question_vector,
            self.document_vectors
        ).flatten()

        ranked_indices = scores.argsort()[::-1]

        results = []

        for index in ranked_indices[:top_k]:
            score = float(scores[index])

            # Avoid returning passages with no matching terms.
            if score <= 0:
                continue

            result = self.passages[index].copy()
            result["score"] = round(score, 3)
            results.append(result)

        return results