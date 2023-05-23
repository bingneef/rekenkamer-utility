from src.util.airflow import (
    check_custom_source_running,
    check_custom_source_scheduled,
    get_source_status,
)
from src.util.db import get_conn_sources
from dataclasses import dataclass, asdict
from src.util.app_engine import (
    remove_documents as remove_documents_app_engine,
    list_engines,
)
from src.util.logger import logger
from src.util.s3 import list_documents, delete_document

table_name = "source_documents"


@dataclass
class Source:
    key: str
    document_count: int
    status: str = None
    start_date: str = None
    end_date: str = None

    @staticmethod
    def list_sources() -> list["Source"]:
        sources = get_conn_sources()[table_name].aggregate(
            [
                {"$match": {"source": {"$ne": "custom"}}},
                {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 100},
            ]
        )

        return [
            Source(key=source["_id"], document_count=source["count"])
            for source in sources
        ]

    @staticmethod
    def list_private_sources(api_key: str) -> list["Source"]:
        engines = list_engines(api_key)

        return [
            Source.get_source(engine, fallback=True)
            for engine in engines
            if engine[:14] == "source-custom-"
        ]

    @staticmethod
    def get_source(source_key: str, fallback=False, check_status=False) -> "Source":
        source_match = {"source": source_key}
        if source_key[:14] == "source-custom-":
            source_match = {"source": "custom", "meta.sub_source": source_key[14:]}

        sources = get_conn_sources()[table_name].aggregate(
            [
                {"$match": source_match},
                {"$group": {"_id": "remote_uid", "count": {"$sum": 1}}},
                {"$limit": 1},
            ],
        )
        sources = list(sources)

        # FIXME: Add documentation
        if len(sources) == 0:
            if fallback:
                status = None
                if check_status:
                    status = "PREPARING"
                    if source_key[:14] == "source-custom-":
                        if not check_custom_source_scheduled(
                            source_key[14:]
                        ) and not check_custom_source_running(source_key[14:]):
                            status = "FAILED"

                return Source(
                    key=source_key,
                    document_count=0,
                    status=status,
                    start_date=None,
                    end_date=None,
                )
            else:
                return None

        source = sources[0]

        # FIXME: Add documentation
        status = None
        if check_status:
            if source_key[:14] == "source-custom-":
                in_progress = check_custom_source_running(source_key[14:])

                if in_progress:
                    status = "IN_PROGRESS"
                elif source["count"] > 0:
                    incomplete_document = get_conn_sources()[table_name].find_one(
                        {**source_match, "stored": False},
                    )

                    if incomplete_document is None:
                        status = "DONE"
                    else:
                        status = "FAILED"
                elif check_custom_source_scheduled(source_key[14:]):
                    status = "PREPARING"
                else:
                    status = "FAILED"

            else:
                status = get_source_status(source_key)

        start_date_doc = get_conn_sources()[table_name].find_one(
            {**source_match, "stored": True}, sort=[("date", 1)]
        )
        end_date_doc = get_conn_sources()[table_name].find_one(
            {**source_match, "stored": True}, sort=[("date", -1)]
        )
        start_date = start_date_doc["date"] if start_date_doc is not None else None
        end_date = end_date_doc["date"] if end_date_doc is not None else None

        return Source(
            key=source_key,
            document_count=source["count"],
            status=status,
            start_date=start_date,
            end_date=end_date,
        )

    def list_documents(self):
        if self.key[:14] != "source-custom-":
            return []

        s3_source_path = f"source--custom/{self.key[14:]}"
        return list_documents(s3_source_path)

    def delete_document(self, filename, api_key):
        doc_id = f"{self.key[14:]}/{filename}"
        resp = remove_documents_app_engine(
            api_key, engine=self.key, ids=[f"custom:{doc_id}"]
        )
        logger.debug(f"Elastic delete: {resp}")

        resp = get_conn_sources()[table_name].delete_one({"_id": f"custom:{doc_id}"})
        logger.debug(f"Deleted documents: {resp.deleted_count}")
        if resp.raw_result["ok"] != 1:
            logger.info(
                f"An error occurred while deleting {filename}: {resp.raw_result}"
            )
            return False

        return delete_document(
            bucket="source--custom", file_path=f"{self.key[14:]}/{filename}"
        )

    @property
    def clean_dict(self):
        data = asdict(self)
        return data
