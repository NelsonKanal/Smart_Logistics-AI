from stage4_rag.retriever import Retriever


def test_knowledge_base_loads_documents():
    retriever = Retriever()

    assert len(retriever.passages) > 0


def test_standard_delivery_question_finds_relevant_passage():
    retriever = Retriever()

    results = retriever.search(
        "How long does standard delivery take?",
        top_k=3
    )

    assert len(results) > 0

    combined_text = " ".join(
        result["text"].lower() for result in results
    )

    assert "five calendar days" in combined_text


def test_damaged_parcel_question_finds_relevant_passage():
    retriever = Retriever()

    results = retriever.search(
        "What should staff do when a parcel is damaged?",
        top_k=3
    )

    assert len(results) > 0

    combined_text = " ".join(
        result["text"].lower() for result in results
    )

    assert "damaged parcel" in combined_text


def test_empty_question_returns_no_results():
    retriever = Retriever()

    assert retriever.search("", top_k=3) == []