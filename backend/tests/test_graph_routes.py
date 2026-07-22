from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def ask(question,
        customer_id="customer-001",
        thread_id="thread-001"):

    response = client.post(
        "/chat",
        json={
            "question": question,
            "customer_id": customer_id,
            "thread_id": thread_id,
        },
    )

    assert response.status_code == 200

    return response.json()

def test_knowledge_route():
    result = ask(
        "What features are included in the Pro plan?"
    )

    assert result["route"] == "knowledge"

    assert result["review"] == "PASS"

    assert result["confidence"] >= 0.85

    assert len(result["sources"]) > 0

    assert result["final_answer"] != ""

def test_troubleshooting_route():
    result = ask(
        "My CSV import keeps failing."
    )

    assert result["route"] == "troubleshooting"

    assert result["priority"] == "normal"

    assert result["assigned_team"] == "technical_support"

    assert result["review"] == "PASS"

def test_escalation_route():
    result = ask(
    "My account has been hacked."
    )

    assert result["route"] == "escalation"

    assert result["priority"] == "urgent"

    assert result["assigned_team"] == "technical_support"

    assert result["review"] == "PASS"

def test_onboarding_route():
    result = ask(
        "Help us migrate from Salesforce."
    )

    assert result["route"] == "onboarding"

    assert result["assigned_team"] == "customer_success"

    assert result["review"] == "PASS"

def test_general_route():
    result = ask(
        "Hello!"
    )

    assert result["route"] == "general"

    assert result["priority"] == "low"

    assert result["assigned_team"] == "customer_support"