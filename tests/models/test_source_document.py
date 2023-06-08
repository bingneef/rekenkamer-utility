import pytest

from src.models.source_document import SourceDocument, table_name
from src.util.db import get_conn_sources


@pytest.mark.parametrize(
    ["path", "expected_output"],
    [
        ["source--rekenkamer/test.txt", "rekenkamer:test"],
        [
            "source--beleids-evaluaties/demo:2020:01:01.pdf",
            "beleids_evaluaties:demo:2020:01:01",
        ],
    ],
)
def test_s3_path_to_id(path, expected_output):
    assert (
        SourceDocument.s3_path_to_id(path) == expected_output
    ), "Correct id from s3_path"


@pytest.mark.parametrize(
    ["paths", "expected_output"],
    [
        [["source--rekenkamer/abc.txt"], [{"_id": "rekenkamer:abc", "title": "ABC"}]],
        [["source--rekenkamer/123.txt"], []],
        [
            ["source--rekenkamer/abc.txt", "source--rekenkamer/123.txt"],
            [{"_id": "rekenkamer:abc", "title": "ABC"}],
        ],
    ],
)
def test_s3_paths_to_documents(paths, expected_output):
    # Add source document to database
    get_conn_sources()[table_name].insert_one({"_id": "rekenkamer:abc", "title": "ABC"})

    output = list(SourceDocument.s3_paths_to_documents(paths, {"title": 1}))
    output.sort()
    expected_output.sort()

    assert output == expected_output, "Correct documents from s3_path"
