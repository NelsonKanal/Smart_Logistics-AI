from pathlib import Path

DOCUMENTS_DIR = Path(__file__).resolve().parent / "documents"


def load_knowledge_base():
    """Load Markdown documents and split them into passages."""
    passages = []

    for file_path in DOCUMENTS_DIR.glob("*.md"):
        text = file_path.read_text(encoding="utf-8")

        # Split the document at blank lines.
        sections = text.split("\n\n")

        for section in sections:
            section = section.strip()

            # Ignore empty sections and Markdown headings.
            if section and not section.startswith("#"):
                passages.append({
                    "source": file_path.name,
                    "text": section
                })

    return passages


if __name__ == "__main__":
    documents = load_knowledge_base()
    print(f"Loaded {len(documents)} passages.")

    for number, document in enumerate(documents, start=1):
        print(f"\nPassage {number}:")
        print(document["text"])