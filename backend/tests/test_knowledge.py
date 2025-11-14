from http import HTTPStatus


def test_add_knowledge_document(client):
    assistant_payload = {"name": "Doc Assistant"}
    assistant_resp = client.post("/api/v1/assistants/", json=assistant_payload)
    assistant_id = assistant_resp.json()["id"]

    knowledge_payload = {"title": "Handbook", "content": "Always be helpful."}
    response = client.post(
        f"/api/v1/assistants/{assistant_id}/knowledge/",
        json=knowledge_payload,
    )
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["title"] == knowledge_payload["title"]

    list_resp = client.get(f"/api/v1/assistants/{assistant_id}/knowledge/")
    assert list_resp.status_code == HTTPStatus.OK
    docs = list_resp.json()
    assert len(docs) == 1
