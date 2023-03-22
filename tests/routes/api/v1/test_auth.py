import requests


def test_signup():
    response = requests.post("http://localhost:5000/api/v1/auth/signup", json={
        'display_name': 'test',
        'email': 'info@example.com',
        'password': 'test',
        'verification_code': '96865e8b'
    })

    assert response.text == 200
    assert response.status_code == 200
    assert list(response.json().keys()).sort() == ['display_name', 'search_api_key', 'document_access_token'].sort()

    assert response.json()['display_name'] == 'test'
    assert response.json()['search_api_key'] == "private-123"

