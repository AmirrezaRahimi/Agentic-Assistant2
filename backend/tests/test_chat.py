from http import HTTPStatus


def test_chat_flow(client):
    assistant_payload = {"name": "Chat Assistant", "description": "desc"}
    assistant_resp = client.post("/api/v1/assistants/", json=assistant_payload)
    assistant_id = assistant_resp.json()["id"]

    chat_payload = {"user_message": "Hello"}
    chat_resp = client.post(f"/api/v1/chat/assistants/{assistant_id}", json=chat_payload)
    assert chat_resp.status_code == HTTPStatus.OK
    data = chat_resp.json()
    assert data["assistant_message"] == "Stubbed response"
    assert data["session"]["assistant_id"] == assistant_id
