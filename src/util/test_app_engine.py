import pytest


@pytest.mark.parametrize(["email", "output"],
                         [
                            ("info@example.com", "info-example-com"),
                            ("info.new@example.com", "info-new-example-com"),
                            ("info+new@example.com", "info-new-example-com")
                         ])
def test_email_to_api_key_name(email, output):
    from .app_engine import _email_to_api_key_name

    assert _email_to_api_key_name(email) == output, "Formatted email correctly"
