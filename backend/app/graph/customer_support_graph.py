import json, re

from typing import Literal, TypedDict
from langchain_core.documents import Document
from langgraph.graph import END, START, StateGraph
from ..services.memory_service import memory_service
from ..services.customer_memory import customer_memory

class AgentState(TypedDict):
    question: str
    customer_id: str
    thread_id: str

    messages: list

    route: str

    documents: list[Document]

    answer: str

    review: str

    confidence: float

    review_scores: dict

    feedback: list[str]

    priority: Literal[
        "low",
        "normal",
        "urgent",
    ]

    assigned_team: str

    sources: list[str]

    memory_updates: list

    final_answer: str


class CustomerSupportGraph:

    def __init__(self, retriever, llm):

        self.retriever = retriever
        self.llm = llm

    # ---------------------------------------------------------
    # Helper
    # ---------------------------------------------------------

    @staticmethod
    def normalize_route(response: str) -> str:

        response = response.lower().strip()

        routes = [
            "knowledge",
            "troubleshooting",
            "escalation",
            "onboarding",
            "general",
        ]

        for route in routes:
            if route in response:
                return route

        return "general"

    # ---------------------------------------------------------
    # Nodes
    # ---------------------------------------------------------

    def classify_request_node(self, state: AgentState):

        question = state["question"]

        prompt = f"""
        You are a request classifier.

        Choose exactly ONE category from this list:

        knowledge
        troubleshooting
        escalation
        onboarding
        general

        Examples:

        Knowledge:
        Questions that require information from the Northstar CRM knowledge base,
        including product features, pricing, plans, documentation,
        integrations, workflows, or policies.
        
        Troubleshooting:
        Questions where something is broken or not working.
        
        Escalation:
        Urgent, sensitive, security, payment, legal, or highly dissatisfied customers.
        
        Onboarding:
        Questions about setup, implementation, migration, training, or getting started.
        
        General:
        Greetings, introductions, thanks, small talk,
        or questions unrelated to the CRM product.

        Rules:
        - Return ONLY one of these five category names.
        - Do not return an example.
        - Do not explain your answer.
        - Do not mention that you are using documentation.
        - Do not explain your reasoning.
        - Answer naturally as a customer support representative.

        Customer Question:
        {question}

        Category:
        """

        response = self.llm.invoke(prompt)
        #print("=" * 60)
        #print("RAW LLM RESPONSE:")
        #print(response.content)
        #print("=" * 60)
        route = self.normalize_route(response.content)
        #print(f"Normalized route: {route}")
        return {
            "route": route
        }


    def retrieve_documents_node(self, state: AgentState):

        question = state["question"]

        documents = self.retriever.invoke(question)

        sources = []

        seen = set()

        for doc in documents:

            source = doc.metadata.get("source", "Unknown")

            if source in seen:
                continue

            seen.add(source)

            sources.append({
                "source": source,
                "content_preview": doc.page_content[:200].replace("\n", " ")
            })

        return {
            "documents": documents,
            "sources": sources
        }

    def generate_answer_node(self, state: AgentState):

        history = memory_service.get_history(
            state["thread_id"]
        )

        conversation = "\n".join(
            f'{item["role"].title()}: {item["content"]}'
            for item in history
        )

        memory = customer_memory.get(
            state["customer_id"]
        )

        memory_text = "\n".join(
            f"{key}: {value}"
            for key, value in memory.items()
        )


        context = "\n\n".join(
            doc.page_content
            for doc in state["documents"]
        )

        prompt = f"""
        You are Northstar CRM's AI Customer Support Assistant.
        
        Customer Request Type

        {state["route"]}

        Instructions
        
        - If the route is knowledge, provide a factual answer using only the retrieved documentation.
        - If the route is troubleshooting, provide ordered troubleshooting steps and explain when escalation is appropriate.
        - If the route is escalation, explain the urgency, include the assigned team, and recommend next steps.
        - If the route is onboarding, generate a practical onboarding plan with checklist and assumptions.
        - If the route is general, answer naturally and honestly.

        Do not mention documentation.
        Do not invent information.
        Be concise and professional.

        Known Customer Information

        {memory_text}
        
        Previous Conversation

        {conversation}
        
        Customer Request Type

        {state["route"]}

        Respond appropriately for this type of request.

        Documentation

        {context}

        Current Customer Question

        {state["question"]}

        Answer:
        """

        response = self.llm.invoke(prompt)

        memory_service.add_user_message(
            state["thread_id"],
            state["question"]
        )

        memory_service.add_assistant_message(
            state["thread_id"],
            response.content
        )

        return {
            "answer": response.content,
            #"memory_updates": history
        }

    def review_answer_node(self, state: AgentState):

        prompt = f"""
        You are a Senior QA Reviewer for Northstar CRM.

        Review the AI-generated answer using the retrieved documentation.

        Customer Question

        {state["question"]}

        AI Answer

        {state["answer"]}

        Evaluate the answer on the following criteria:

        Accuracy (1-5)
        - 5 = Every statement is supported by documentation.
        - 3 = Mostly correct but minor uncertainty.
        - 1 = Contains unsupported or incorrect claims.

        Completeness (1-5)
        - 5 = Fully answers the customer's question.
        - 3 = Partially answers.
        - 1 = Important information is missing.

        Groundedness (1-5)
        - 5 = Uses only documented information.
        - 3 = Small assumptions.
        - 1 = Hallucinated information.

       Professionalism (1-5)
        - 5 = Clear, concise and professional.
        - 3 = Understandable but could improve.
        - 1 = Poor quality response.

        Decision Rules

        PASS
        - Accuracy >= 4
        - Groundedness >= 4
        - Average score >= 4
        
        FAIL
        - Any hallucination
        - Accuracy <= 2
        - Groundedness <= 2
        
        Return ONLY valid JSON.
        
        {{
            "status":"PASS",
            "scores": {{
                "accuracy":5,
                "completeness":5,
                "groundedness":5,
                "professionalism":5
            }},
            "feedback":[]
        }}
        """

        response = self.llm.invoke(prompt)

        print("=" * 80)
        print("RAW REVIEW RESPONSE")
        print(response.content)
        print("=" * 80)

        match = re.search(r"\{[\s\S]*\}", response.content)

        if not match:
            raise ValueError("Reviewer did not return JSON.")

        result = json.loads(match.group())

        print("=" * 80)
        print("PARSED RESULT")
        print(result)
        print("=" * 80)

        scores = result["scores"]

        confidence = (
                             scores["accuracy"]
                             + scores["completeness"]
                             + scores["groundedness"]
                             + scores["professionalism"]
                     ) / 20

        return {
            "review": result["status"],
            "confidence": confidence,
            "feedback": result["feedback"]
        }

    #def review_router(self, state: AgentState):

        if state["review"] == "PASS":
            return "finalize"

        return "regenerate"

    def finalize_node(self, state: AgentState):

        return {
            "final_answer": state["answer"]
        }

    def regenerate_answer_node(self, state: AgentState):

        feedback = "\n".join(
            state.get("feedback", [])
        )

        prompt = f"""
        You are rewriting a customer support response.

        Customer Question

        {state["question"]}

        Previous Answer

        {state["answer"]}

        Reviewer Feedback

        {feedback}

        Rewrite the answer.

        Do not ignore reviewer comments.
        """

        response = self.llm.invoke(prompt)

        return {
            "answer": response.content
        }

    def troubleshooting_node(self, state: AgentState):

        return {
            "priority": "normal",
            "assigned_team": "technical_support",
        }

    def escalation_node(self, state: AgentState):

        return {
            "priority": "urgent",
            "assigned_team": "technical_support",
        }

    def onboarding_node(self, state: AgentState):

        return {
            "priority": "normal",
            "assigned_team": "customer_success",
        }

    def general_node(self, state: AgentState):

        return {
            "priority": "low",
            "assigned_team": "customer_support",
        }

    def extract_customer_memory_node(self, state: AgentState):

        question = state["question"].lower()

        updates = {}

        if "enterprise" in question:
            updates["plan"] = "Enterprise"

        elif "pro plan" in question:
            updates["plan"] = "Pro"

        elif "starter plan" in question:
            updates["plan"] = "Starter"

        if "sales team" in question:
            updates["company_type"] = "Sales"

        if "migration" in question:
            updates["goal"] = "Migration"

        if "onboarding" in question:
            updates["goal"] = "Onboarding"

        if updates:
            customer_memory.update(
                state["customer_id"],
                updates
            )

        return {}

    # ---------------------------------------------------------
    # Router
    # ---------------------------------------------------------

    @staticmethod
    def route_request(
        state: AgentState,
    ) -> Literal[
        "knowledge",
        "troubleshooting",
        "escalation",
        "onboarding",
        "general",
    ]:

        return state["route"]

    def review_router(self, state: AgentState):

        if state["confidence"] >= 0.85:
            return "finalize"

        return "regenerate"

    # ---------------------------------------------------------
    # Build Graph
    # ---------------------------------------------------------

    def build(self):

        builder = StateGraph(AgentState)

        builder.add_node(
            "classify_request",
            self.classify_request_node,
        )

        #builder.add_node("knowledge", self.knowledge_node )

        builder.add_node("retrieve_documents", self.retrieve_documents_node)
        builder.add_node("generate_answer", self.generate_answer_node)
        builder.add_node("review_answer", self.review_answer_node)
        builder.add_node("regenerate_answer", self.regenerate_answer_node)
        builder.add_node("finalize", self.finalize_node)
        builder.add_node("extract_customer_memory",self.extract_customer_memory_node)
        builder.add_node("troubleshooting",self.troubleshooting_node)

        builder.add_node("escalation", self.escalation_node )

        builder.add_node("onboarding",self.onboarding_node )

        builder.add_node("general", self.general_node)

        builder.add_edge(
            START,
            "classify_request",
        )

        builder.add_conditional_edges(
            "classify_request",
            self.route_request,
            {
                "knowledge": "retrieve_documents",
                "troubleshooting": "troubleshooting",
                "escalation": "escalation",
                "onboarding": "onboarding",
                "general": "general",
            },
        )

        # ----------------------------------------------------
        # Knowledge Workflow
        # ----------------------------------------------------

        #builder.add_edge("retrieve_documents", "generate_answer")

        builder.add_edge("retrieve_documents","extract_customer_memory")

        builder.add_edge("extract_customer_memory","generate_answer")

        builder.add_edge("generate_answer","review_answer")

        builder.add_conditional_edges("review_answer",
            self.review_router,
            {
                "finalize": "finalize",
                "regenerate": "regenerate_answer",
            },
        )

        builder.add_edge("regenerate_answer","review_answer")

        builder.add_edge("finalize", END)
        builder.add_edge("troubleshooting", "retrieve_documents")
        builder.add_edge("escalation", "retrieve_documents")
        builder.add_edge("onboarding", "retrieve_documents")
        builder.add_edge("general", "retrieve_documents")

        return builder.compile()


def build_graph(retriever, llm):

    graph = CustomerSupportGraph(
        retriever=retriever,
        llm=llm,
    )

    return graph.build()