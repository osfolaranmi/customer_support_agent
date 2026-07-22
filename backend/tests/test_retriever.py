from pathlib import Path

from app.services.document_loader import load_documents
from app.services.vector_store import create_retriever


def test_retriever():

    backend_dir = Path(__file__).resolve().parents[1]

    knowledgebase = backend_dir / "knowledgebase"

    documents = load_documents(knowledgebase)

    retriever = create_retriever(documents)

    results = retriever.invoke(
        "What is included in the Pro plan?"
    )

    assert len(results) > 0

    for doc in results:
        print(doc.metadata["source"])
        print(doc.page_content[:300])
        print("=" * 60)