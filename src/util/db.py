import os

import pymongo
from dotenv import load_dotenv

load_dotenv()


def get_conn_auth():
    client = pymongo.MongoClient(os.environ["MONGO_CONNECTION_STRING_AUTH"])  # type: ignore

    db_name = os.environ.get("MONGO_DB", "auth")
    if os.environ.get("ENV", "production") == "test":
        db_name = "test_auth"

    db_conn = client[db_name]

    return db_conn


def get_conn_sources():
    client = pymongo.MongoClient(os.environ["MONGO_CONNECTION_STRING_SOURCES"])  # type: ignore

    db_name = os.environ.get("MONGO_DB_SOURCES", "sources")
    if os.environ.get("ENV", "production") == "test":
        db_name = "test_sources"

    db_conn = client[db_name]

    return db_conn


def drop_db():
    if os.environ.get("ENV", "production") != "test":
        raise Exception("You can only drop the test database")

    # Drop auth
    client = pymongo.MongoClient(os.environ["MONGO_CONNECTION_STRING_AUTH"])  # type: ignore
    client.drop_database("test_auth")

    # Drop sources
    client = pymongo.MongoClient(os.environ["MONGO_CONNECTION_STRING_SOURCES"])  # type: ignore
    client.drop_database("test_sources")
