import pytest


@pytest.mark.parametrize(
    ["email", "output"],
    [
        ("info@example.com", "info-example-com-cb3045d1eb66dda5eae9ae2f96edeee9"),
        (
            "info.new@example.com",
            "info-new-example-com-4a212fce46b5f5ca4279d8a5c49a4e35",
        ),
        (
            "info+new@example.com",
            "info-new-example-com-9c18eb4b2a1c0e77f974f2e344d51607",
        ),
    ],
)
def test_email_to_api_key_name(email, output):
    from src.util.app_engine import _email_to_api_key_name

    assert _email_to_api_key_name(email) == output, "Formatted email correctly"
