from pathlib import Path
from typing import List

from langchain_core.documents import Document


def load_documents(folder: Path) -> List[Document]:
    documents = []

    for file in folder.glob("*.txt"):
        documents.append(
            Document(
                page_content=file.read_text(encoding="utf-8"),
                metadata={
                    "source": file.name
                }
            )
        )

    return documents