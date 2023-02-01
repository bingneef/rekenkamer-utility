import os

from minio import Minio

MINIO_HOST = os.getenv('MINIO_HOST', "localhost:9000")
MINIO_ACCESS_KEY = os.getenv('MINIO_ACCESS_KEY', "airflow")
MINIO_SECRET_KEY = os.getenv('MINIO_SECRET_KEY', "airflow1")
MINIO_SECURE = os.getenv('MINIO_SECURE', 0)


def get_client():
    return Minio(
        MINIO_HOST,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE == 1
    )


def get_document(path):
    client = get_client()
    response = None

    bucket_name = path.split('/')[0]
    object_name = "/".join(path.split('/')[1:])

    try:
        response = client.get_object(
            bucket_name=bucket_name,
            object_name=object_name
        )
        doc_body = response.data
    finally:
        if response is not None:
            # Close the connection
            response.close()
            response.release_conn()

    return doc_body
