import pytest

from src.util.db import drop_db


@pytest.fixture(autouse=True)
def start_clean():
    drop_db()

    yield
