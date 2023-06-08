import requests

from src.util.logger import logger


def test_signup(client):
    response = client.post(
        "/api/v1/auth/signup",
        json={
            "display_name": "test",
            "email": "info@example.com",
            "password": "test",
            "verification_code": "96865e8b",
        },
    )

    assert response.status_code == 200

    response_json_keys = list(response.json.keys())
    response_json_keys.sort()
    expected_response_json_keys = [
        "display_name",
        "search_api_key",
        "document_access_token",
        "email",
    ]
    expected_response_json_keys.sort()
    assert response_json_keys == expected_response_json_keys

    assert response.json["display_name"] == "test"
    assert response.json["search_api_key"] == "private-123"
