from http import HTTPStatus


def test_create_and_list_assistants(client):
    payload = {"name": "Test Assistant", "description": "desc"}
    response = client.post("/api/v1/assistants/", json=payload)
    assert response.status_code == HTTPStatus.CREATED
    data = response.json()
    assert data["name"] == payload["name"]

    list_response = client.get("/api/v1/assistants/")
    assert list_response.status_code == HTTPStatus.OK
    assistants = list_response.json()
    assert len(assistants) == 1
    assert assistants[0]["name"] == payload["name"]
