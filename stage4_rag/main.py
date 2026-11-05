from stage4_rag.retriever import Retriever


def answer_question(retriever, question):
    """Find relevant company-policy passages."""
    results = retriever.search(question, top_k=3)

    if not results:
        return (
            "I could not find relevant information in the "
            "current company documents. Please check with "
            "the appropriate team."
        )

    answer_parts = [
        "Here is the most relevant information I found:\n"
    ]

    for number, result in enumerate(results, start=1):
        answer_parts.append(
            f"\nResult {number}\n"
            f"Source: {result['source']}\n"
            f"Relevance score: {result['score']}\n"
            f"Information: {result['text']}\n"
        )

    answer_parts.append(
        "\nNote: These are retrieved document passages, "
        "not a guarantee that every part of your question "
        "has been answered."
    )

    return "\n".join(answer_parts)


def main():
    print("=" * 45)
    print(" SMARTLOGISTICS AI - RAG ASSISTANT")
    print("=" * 45)

    try:
        retriever = Retriever()
    except (ValueError, OSError) as error:
        print(f"Could not load the knowledge base: {error}")
        return

    print(f"Knowledge base loaded: {len(retriever.passages)} passages")
    print("\nAsk questions about delivery policies.")
    print("Type 'exit' to close the assistant.")

    while True:
        question = input("\nYour question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("SmartLogistics RAG assistant stopped.")
            break

        if not question:
            print("Please enter a question.")
            continue

        response = answer_question(retriever, question)
        print("\n" + response)


if __name__ == "__main__":
    main()