import pytest

from .zip import unique_custom_engines


@pytest.mark.parametrize(["paths", "expected_output"],
                         [
                             (['source--main/test.txt'], []),
                             (['source--main/test.txt', 'source--custom/toeter/doc.txt'], ['toeter']),
                             (['source--custom/toeter/doc.txt', 'source--custom/toeter/doc2.txt'], ['toeter']),
                             (['source--custom/toeter/doc.txt', 'source--custom/reutel/doc.txt'], ['toeter', 'reutel'])
                         ])
def test_source_bucket_name(paths, expected_output):
    assert unique_custom_engines(paths).sort() == expected_output.sort(), "Retrieve unique custom engines"
