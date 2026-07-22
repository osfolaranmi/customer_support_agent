from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_ollama import ChatOllama

from .api.chat_route import router as chat_router
from .api.health_route import router as health_router
from .services.document_loader import load_documents
from .services.vector_store import create_retriever
from .graph.customer_support_graph import build_graph

# -----------------------------------------------------------------------------
# Project Paths
# -----------------------------------------------------------------------------

# backend/
BACKEND_DIR = Path(__file__).resolve().parents[1]

# backend/.env
ENV_FILE = BACKEND_DIR / ".env"

# backend/knowledgebase
KNOWLEDGEBASE_DIR = BACKEND_DIR / "knowledgebase"

# -----------------------------------------------------------------------------
# Load Environment Variables
# -----------------------------------------------------------------------------

load_dotenv(ENV_FILE)

# -----------------------------------------------------------------------------
# Initialize Knowledge Base & Retriever
# -----------------------------------------------------------------------------

documents = load_documents(KNOWLEDGEBASE_DIR)
retriever = create_retriever(documents)


#-------------------------------------------------------------------------
# OLLAMA Model
#----------------------------------------
import os

MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3")

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0
)

#-------------------------------------------------------------------------
# Build LangGraph
#-------------------------------------------------------------------------
print("Creating LangGraph...")
graph = build_graph(
    retriever=retriever,
    llm=llm
)
print("Graph created successfully.")
# -----------------------------------------------------------------------------
# FastAPI Application
# -----------------------------------------------------------------------------

app = FastAPI(
    title="Northstar CRM Customer Support Agent",
    version="1.0.0",
)

app.state.graph = graph

print("Graph added to app.state")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# Routes
# -----------------------------------------------------------------------------

app.include_router(health_router)
app.include_router(chat_router)