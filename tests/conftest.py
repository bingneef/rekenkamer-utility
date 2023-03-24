import pytest

from src.util.db import drop_db
from main import create_app


@pytest.fixture(autouse=True)
def start_clean():
    drop_db()

    yield


@pytest.fixture
def client():
    app = create_app()
    app.config.update({'TESTING': True})

    with app.test_client() as client:
        yield client
