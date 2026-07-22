from langchain_chroma import Chroma

from langchain_text_splitters import RecursiveCharacterTextSplitter

from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")

from langchain_huggingface import HuggingFaceEmbeddings



def create_retriever(documents):
    splitter = RecursiveCharacterTextSplitter(

        chunk_size=1000,

        chunk_overlap=200
    )
    VECTOR_DB = Path("./vector_store")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    chunks = splitter.split_documents(documents)

    if VECTOR_DB.exists():
        vector_store = Chroma(
            collection_name="northstar_support",
            embedding_function=embeddings,
            persist_directory=str(VECTOR_DB)
        )
    else:
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name="northstar_support",
            persist_directory=str(VECTOR_DB)
        )

    return vector_store.as_retriever(
        search_kwargs={"k": 5}
    )