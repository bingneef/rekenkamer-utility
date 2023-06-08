import pytest
from src.util.db import get_conn_sources


@pytest.mark.parametrize(
    ["source", "expected_output"],
    [
        ["rekenkamer", "Rekenkamer"],
        [
            "kamerstukken_schriftelijke_vragen_antwoord",
            "Kamerstukken schriftelijke vragen antwoord",
        ],
    ],
)
def test_source_bucket_name(source, expected_output):
    from src.util.zip import _prettify_source

    assert _prettify_source(source) == expected_output, "Expected prettified source"


@pytest.mark.parametrize(
    ["s3_path", "expected_output"],
    [
        ["source--custom/xxx/X.pdf", "xxx/X.pdf"],
        ["source--custom/yyy/y.xlsx", "yyy/y.xlsx"],
    ],
)
def test_format_custom_filename(s3_path, expected_output):
    from src.util.zip import _format_custom_filename

    assert (
        _format_custom_filename(s3_path) == expected_output
    ), "Expected formatted filename"


@pytest.mark.parametrize(
    ["s3_path", "expected_output"],
    [
        ["source--rekenkamer/abc.pdf", "Rekenkamer - abc (149d16c7).pdf"],
        [
            "source--kamerstukken-schriftelijke-vragen-antwoord/xyz.xlsx",
            "Kamerstukken schriftelijke vragen antwoord - xyz (3e6b109c).xlsx",
        ],
    ],
)
def test_format_public_filename(s3_path, expected_output):
    from src.util.zip import _format_public_filename

    assert (
        _format_public_filename(s3_path) == expected_output
    ), "Expected formatted filename"


@pytest.mark.parametrize(
    ["s3_paths", "expected_output"],
    [
        [
            ["source--rekenkamer/abc.pdf"],
            [("source--rekenkamer/abc.pdf", "Rekenkamer - ABC (149d16c7).pdf")],
        ],
        [
            ["source--kamerstukken-schriftelijke-vragen-antwoord/xyz.xlsx"],
            [
                (
                    "source--kamerstukken-schriftelijke-vragen-antwoord/xyz.xlsx",
                    "Kamerstukken schriftelijke vragen antwoord - XYZ (3e6b109c).xlsx",
                )
            ],
        ],
        [
            ["source--rekenkamer/123.pdf"],
            [("source--rekenkamer/123.pdf", "Rekenkamer - 123 (8235fa44).pdf")],
        ],
        [
            ["source--custom/xxx/X.pdf"],
            [("source--custom/xxx/X.pdf", "xxx/X.pdf")],
        ],
        [
            ["source--rekenkamer/abc.pdf", "source--custom/xxx/X.pdf"],
            [
                ("source--rekenkamer/abc.pdf", "Rekenkamer - ABC (149d16c7).pdf"),
                ("source--custom/xxx/X.pdf", "xxx/X.pdf"),
            ],
        ],
    ],
)
def test_paths_with_filename(s3_paths, expected_output):
    from src.util.zip import paths_with_filename
    from src.models.source_document import table_name

    # Add source document to database
    get_conn_sources()[table_name].insert_many(
        [
            {"_id": "rekenkamer:abc", "title": "ABC"},
            {
                "_id": "kamerstukken_schriftelijke_vragen_antwoord:xyz",
                "title": "XYZ",
            },
        ]
    )

    output = paths_with_filename(s3_paths)
    output.sort()
    expected_output.sort()

    assert output == expected_output, "Expected formatted filename"
