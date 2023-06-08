from src.util.db import get_conn_sources


table_name = "source_documents"


class SourceDocument:
    @staticmethod
    def s3_paths_to_documents(
        s3_paths: list[str], document_fields: dict[str, int] = {}
    ):
        ids = [SourceDocument.s3_path_to_id(s3_path) for s3_path in s3_paths]
        return get_conn_sources()[table_name].find(
            {"_id": {"$in": ids}}, document_fields
        )

    @staticmethod
    def s3_path_to_id(s3_path: str) -> str:
        source = s3_path.split("/")[0].replace("source--", "").replace("-", "_")
        filepath = s3_path.split("/")[1]
        return f"{source}:{filepath.split('.')[0]}"
