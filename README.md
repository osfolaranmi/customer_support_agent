# Northstar Customer Support Agent

An AI-powered customer support assistant built with **FastAPI**, **LangGraph**, **Ollama**, **ChromaDB**, and **Next.js**.

The application uses **Retrieval-Augmented Generation (RAG)**, **Agentic AI workflows**, and **customer memory** to provide accurate, context-aware responses to customer support queries.

---

## Overview

Northstar Customer Support Agent is designed to simulate an intelligent customer support representative capable of:

- Understanding customer intent
- Retrieving relevant knowledge base documents
- Remembering previous conversations
- Remembering customer preferences
- Reviewing its own responses before replying
- Routing requests to the appropriate support team

The project demonstrates modern Agentic AI concepts including:

- LangGraph agent orchestration
- Retrieval-Augmented Generation (RAG)
- Long-term and short-term memory
- AI self-review
- Response regeneration
- Source attribution

---

# Features

## Intelligent Request Classification

Customer requests are automatically classified into one of five categories:

- Knowledge
- Troubleshooting
- Onboarding
- Escalation
- General

---

## Retrieval-Augmented Generation (RAG)

The assistant retrieves relevant information from a Chroma vector database before generating responses.

Knowledge Base:

- Product documentation
- Pricing
- Subscription plans
- Features
- Integrations
- Support articles

---

## Conversation Memory

Maintains context throughout a conversation using LangGraph thread memory.

Example:

Customer:

> What is included in the Pro plan?

Later:

> How much does it cost?

The assistant understands that "it" refers to the Pro plan.

---

## Customer Memory

Stores customer-specific information across multiple conversations.

Examples:

- Company name
- CRM currently used
- Preferred plan
- Previous issues

This enables more personalized responses.

---

## AI Response Review

Every generated response is reviewed by a second LLM.

The reviewer evaluates:

- Accuracy
- Completeness
- Groundedness
- Professionalism

If the review fails, the response is regenerated automatically.

---

## Source Attribution

Responses include the documentation sources used during retrieval.

Example:

```
Sources:

pricing.txt
subscription_plans.txt
```

---

## Metadata

Each response includes:

- Route
- Confidence score
- Review scores
- Assigned support team
- Priority
- Feedback
- Sources

---

# Technology Stack

## Backend

- Python
- FastAPI
- LangGraph
- LangChain
- Ollama
- ChromaDB
- Pydantic

## Frontend

- Next.js
- React
- TypeScript

## Embeddings

- sentence-transformers/all-MiniLM-L6-v2

---

# Project Architecture

```
                    User
                     │
                     ▼
             Next.js Frontend
                     │
                     ▼
                FastAPI API
                     │
                     ▼
               LangGraph Agent
                     │
      ┌──────────────┼──────────────┐
      ▼              ▼              ▼
 Request       Customer Memory   ChromaDB
Classifier                         (RAG)
      │              │              │
      └──────────────┼──────────────┘
                     ▼
             Response Generator
                     │
                     ▼
              AI Review Agent
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
      PASS                  Regenerate
          │                     │
          └──────────┬──────────┘
                     ▼
              Final Response
```

---

# LangGraph Workflow

```
START
   │
   ▼
Classify Request
   │
   ▼
Retrieve Documents
   │
   ▼
Retrieve Customer Memory
   │
   ▼
Generate Response
   │
   ▼
Review Response
   │
 ┌─┴──────────────┐
 │                │
PASS            FAIL
 │                │
 ▼                │
Finalize ◄────────┘
 │
 ▼
END


flowchart TD

    START([Start])

    CLASSIFY["Classify Request"]

    ROUTER{"Request Type"}

    KNOWLEDGE["Knowledge"]

    TROUBLE["Troubleshooting"]

    ESCALATION["Escalation"]

    ONBOARDING["Onboarding"]

    GENERAL["General"]

    RETRIEVE["Retrieve Documents"]

    MEMORY["Extract Customer Memory"]

    GENERATE["Generate Answer"]

    REVIEW["Review Answer"]

    FINALIZE["Finalize Response"]

    REGENERATE["Regenerate Answer"]

    END([End])

    START --> CLASSIFY

    CLASSIFY --> ROUTER

    ROUTER -->|Knowledge| RETRIEVE
    ROUTER -->|Troubleshooting| TROUBLE
    ROUTER -->|Escalation| ESCALATION
    ROUTER -->|Onboarding| ONBOARDING
    ROUTER -->|General| GENERAL

    TROUBLE --> RETRIEVE
    ESCALATION --> RETRIEVE
    ONBOARDING --> RETRIEVE
    GENERAL --> RETRIEVE

    RETRIEVE --> MEMORY

    MEMORY --> GENERATE

    GENERATE --> REVIEW

    REVIEW -->|PASS| FINALIZE

    REVIEW -->|FAIL| REGENERATE

    REGENERATE --> REVIEW

    FINALIZE --> END
```

---

# Project Structure

```
backend/
│
├── app/
│   ├── api/
│   ├── graph/
│   ├── services/
│   ├── schemas/
│   ├── util/
│   └── main.py
│
├── knowledgebase/
├── tests/
├── vector_store/
├── requirements.txt
└── .env

frontend/
│
├── app/
├── components/
├── services/
└── package.json
```

---

# Installation

## Clone Repository

```bash
git clone https://github.com/osfolaranmi/customer_support_agent.git

cd customer-support-agent
```

---

## Backend Setup

Create a virtual environment.

```bash
python -m venv .venv
```

Activate it.

Windows

```bash
.venv\Scripts\activate
```

Install dependencies.

```bash
pip install -r requirements.txt
```

---

## Install Ollama

Download Ollama.

https://ollama.com

Pull the model.

```bash
ollama pull llama3
```

---

## Environment Variables

Create a `.env` file.

Example:

```text
OLLAMA_MODEL=llama3

CHROMA_DB=./vector_store

KNOWLEDGE_BASE=./knowledgebase
```

---

## Start Backend

```bash
uvicorn app.main:app --reload
```

Backend runs on:

```
http://localhost:8000
```

Swagger:

```
http://localhost:8000/docs
```

---

## Frontend Setup

```
cd frontend
```

Install packages.

```bash
npm install
```

Run.

```bash
npm run dev
```

Frontend:

```
http://localhost:3000
```

---

# Running Tests

Run all tests.

```bash
pytest -v
```

Current test coverage includes:

- Request routing
- Knowledge retrieval
- Troubleshooting
- Escalation
- Onboarding
- General requests
- Conversation memory
- Customer memory

Example:

```
5 passed in 793 seconds
```

---

# Example Questions

## Knowledge

> What is included in the Pro plan?
<img width="1628" height="999" alt="image" src="https://github.com/user-attachments/assets/c4bc198e-f623-448e-b617-dd4720bcc03e" />
---

## Troubleshooting

> Why am I seeing duplicate contacts after import?
<img width="913" height="962" alt="image" src="https://github.com/user-attachments/assets/1ab40914-e029-492c-aa69-94989353ce6d" />
---

## Onboarding

> We are migrating from spreadsheets. What setup checklist should we follow?
<img width="1093" height="969" alt="image" src="https://github.com/user-attachments/assets/26402f6a-3e5a-45b1-9668-0f5e664b7492" />

---

## Escalation

> I think someone accessed our account without permission.
<img width="973" height="991" alt="image" src="https://github.com/user-attachments/assets/6998297a-82b2-46ed-a665-46962c44dc89" />

---

## General

> Hello!
<img width="1002" height="527" alt="image" src="https://github.com/user-attachments/assets/0a0a286d-c341-457e-a07b-3741930befe3" />

---

## Conversation Memory 
> Follow-up question using memory
<img width="938" height="994" alt="image" src="https://github.com/user-attachments/assets/6fd39b0f-3dc5-43a2-bb85-96b80618826a" />

---

# Future Improvements

Potential enhancements include:

- Multi-agent workflows
- Human-in-the-loop approval
- Ticket creation
- CRM integration
- Authentication
- Streaming responses
- Feedback learning
- Analytics dashboard

---

# Lessons Learned

This project demonstrates practical implementation of Agentic AI concepts including:

- LangGraph workflows
- Retrieval-Augmented Generation
- Vector databases
- Customer memory
- AI self-review
- Multi-step reasoning
- Production API development
- Frontend integration

---

# Author

**Oluwatosin Simeon Folaranmi**

Backend Developer | AI Engineer

Built as part of the **UnlimitedCode Agentic AI Bootcamp Capstone Project**.
