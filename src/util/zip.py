import zipfile
import io
from src.models.source_document import SourceDocument

from src.util.tools import hashed_filename, partition
from .s3 import get_document


def _prettify_source(source: str) -> str:
    return source.replace("_", " ").replace("-", " ").capitalize()


def _format_custom_filename(s3_path: str) -> str:
    filename = s3_path.split("/")[-1]
    custom_source = s3_path.split("/")[1]
    return f"{custom_source}/{filename}"


def _format_public_filename(s3_path: str, title: str | None = None) -> str:
    extension = s3_path.split(".")[-1]

    # Format filename for
    source = s3_path.split("/")[0].replace("source--", "")

    # Set title from s3_path is not set
    title = title or s3_path.split("/")[-1].split(".")[0]

    # Add hash to prevent collisions
    raw_file_name = f"{_prettify_source(source)} - {title}.{extension}"
    return hashed_filename(raw_file_name, s3_path)


def format_filename(s3_path: str, title: str | None = None) -> str:
    if s3_path[:14] == "source--custom":
        return _format_custom_filename(s3_path)

    return _format_public_filename(s3_path, title)


def _map_public_s3_path_with_title(
    s3_path: str, mapping: dict[str, str]
) -> tuple[str, str]:
    # If title is not found, return it as
    title = None

    id = SourceDocument.s3_path_to_id(s3_path)
    if id in mapping.keys():
        title = mapping[id]

    return s3_path, format_filename(s3_path, title)


def custom_paths_with_filename(custom_s3_paths: str) -> tuple[str, str]:
    if any(
        [custom_s3_path[:14] != "source--custom" for custom_s3_path in custom_s3_paths]
    ):
        raise ValueError("All paths must be custom paths")

    return [
        (custom_s3_path, format_filename(custom_s3_path))
        for custom_s3_path in custom_s3_paths
    ]


def public_paths_with_filename(public_s3_paths: list[str]) -> tuple[str, str]:
    if any(
        [public_s3_path[:14] == "source--custom" for public_s3_path in public_s3_paths]
    ):
        raise ValueError("All paths must be public paths")

    # Fetch documents from database for s3_paths and retrieve title
    documents = SourceDocument.s3_paths_to_documents(
        public_s3_paths, {"title": 1, "_id": 1}
    )

    # Dict to map id to title
    mapper = {document["_id"]: document["title"] for document in documents}
    return [
        _map_public_s3_path_with_title(s3_path, mapper) for s3_path in public_s3_paths
    ]


def paths_with_filename(paths: list[str]) -> list[tuple[str, str]]:
    custom_paths, public_paths = partition(
        lambda path: path[:14] == "source--custom", paths
    )

    return [
        *custom_paths_with_filename(custom_paths),
        *public_paths_with_filename(public_paths),
    ]


def generate_zip_buffer(paths: list[str]) -> io.BytesIO:
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        for path, filename in paths_with_filename(paths):
            zip_file.writestr(filename, get_document(path))

    zip_buffer.seek(0)
    return zip_buffer
