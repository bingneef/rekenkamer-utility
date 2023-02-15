import os

import pymongo
from dotenv import load_dotenv

load_dotenv()


def get_conn():
    client = pymongo.MongoClient(os.environ['MONGO_CONNECTION_STRING'])  # type: ignore

    db_name = os.environ.get('MONGO_DB', 'auth')
    db_conn = client[db_name]

    return db_conn
