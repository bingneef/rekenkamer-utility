import pytest

from src.models.source import Source


@pytest.mark.parametrize(
    ["paths", "expected_output"],
    [
        (["source--main/test.txt"], []),
        (["source--main/test.txt", "source--custom/toeter/doc.txt"], ["toeter"]),
        (
            ["source--custom/toeter/doc.txt", "source--custom/toeter/doc2.txt"],
            ["toeter"],
        ),
        (
            ["source--custom/toeter/doc.txt", "source--custom/reutel/doc.txt"],
            ["toeter", "reutel"],
        ),
    ],
)
def test_source_bucket_name(paths, expected_output):
    output = Source.unique_custom_engines(paths)
    output.sort()
    expected_output.sort()

    assert output == expected_output, "Retrieve unique custom engines"
