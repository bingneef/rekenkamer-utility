from src.util.db import get_conn_sources
from dataclasses import dataclass, asdict
from src.util.app_engine import remove_documents as remove_documents_app_engine, list_engines
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
    def list_sources() -> list['Source']:
        sources = get_conn_sources()[table_name].aggregate(
            [
                {"$match": {"source": {"$ne": "custom"}}},
                {"$group": {"_id": "$source", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}},
                {"$limit": 100}
            ]
        )

        return [Source(key=source['_id'], document_count=source['count']) for source in sources]

    @staticmethod
    def list_private_sources(api_key: str) -> list['Source']:
        engines = list_engines(api_key)
        return list(
            map(
                lambda engine: Source.get_source(engine, fallback=True),
                engines
            )
        )

    @staticmethod
    def get_source(source_key: str, fallback=False) -> 'Source':
        source_match = {"source": source_key}
        if source_key[:14] == 'source-custom-':
            source_match = {"source": "custom", "meta.sub_source": source_key[14:]}

        sources = get_conn_sources()[table_name].aggregate(
            [
                {"$match": source_match},
                {"$group": {"_id": "remote_uid", "count": {"$sum": 1}}},
                {"$limit": 1}
            ],
        )
        sources = list(sources)

        if len(sources) is 0:
            if fallback:
                return Source(
                    key=source_key,
                    document_count=0,
                    status="PREPARING",
                    start_date=None,
                    end_date=None,
                )
            else:
                return None

        source = sources[0]

        running_document = get_conn_sources()[table_name].find_one(
            {**source_match, "stored": False},
        )
        start_date = get_conn_sources()[table_name].find_one(
            {**source_match, "stored": True},
            sort=[("date", 1)]
        )
        end_date = get_conn_sources()[table_name].find_one(
            {**source_match, "stored": True},
            sort=[("date", -1)]
        )

        if start_date is None:
            start_date = {'date': None}
        if end_date is None:
            end_date = {'date': None}


        status = "DONE" if running_document is None else "IN_PROGRESS"
        return Source(
            key=source_key,
            document_count=source['count'],
            status=status,
            start_date=start_date['date'],
            end_date=end_date['date'],
        )

    def list_documents(self):
        if self.key[:14] != 'source-custom-':
            return []

        s3_source_path = f"source--custom/{self.key[14:]}"
        return list_documents(s3_source_path)

    def delete_document(self, filename, api_key):
        doc_id = f"{self.key[14:]}/{filename}"
        resp = remove_documents_app_engine(api_key, engine=self.key, ids=[f"custom:{doc_id}"])
        logger.debug(f"Elastic delete: {resp}")

        resp = get_conn_sources()[table_name].delete_one({
            '_id': f"custom:{doc_id}"
        })
        logger.debug(f"Deleted documents: {resp.deleted_count}")
        if resp.raw_result['ok'] != 1:
            logger.info(f"An error occurred while deleting {filename}: {resp.raw_result}")
            return False

        return delete_document(bucket="source--custom", file_path=f"{self.key[14:]}/{filename}")

    @property
    def clean_dict(self):
        data = asdict(self)
        return data
