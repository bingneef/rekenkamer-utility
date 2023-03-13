import pytest
from unittest import mock
import os


@mock.patch.dict(os.environ, {"SECRET_KEY": "12345678901234567890123456789012"}, clear=True)
@pytest.mark.parametrize(["email", "output"],
                         [
                            ("info@example.com", "96865e8b"),
                            ("info.new@example.com", "9731ab7b"),
                            ("info+new@example.com", "2abee3b6")
                         ])
def test_get_verification_code(email, output):
    from .auth import get_verification_code

    assert get_verification_code(email) == output, "Generated verification code correctly"
