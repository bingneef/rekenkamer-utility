import requests

from src.util.logger import logger


def test_signup(client):
    response = client.post("/api/v1/auth/signup", json={
        'display_name': 'test',
        'email': 'info@example.com',
        'password': 'test',
        'verification_code': '96865e8b'
    })

    assert response.status_code == 200
    assert list(response.json.keys()).sort() == ['display_name', 'search_api_key', 'document_access_token'].sort()

    assert response.json['display_name'] == 'test'
    assert response.json['search_api_key'] == "private-123"

