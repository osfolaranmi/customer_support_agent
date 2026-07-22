import os
from langchain_ollama import ChatOllama

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)