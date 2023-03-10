import requests


def test_healthcheck():
    response = requests.get("http://localhost:5000/healthcheck")

    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
