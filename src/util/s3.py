import os

from src.util.log import logging

from minio import Minio
from datetime import timedelta

MINIO_HOST = os.getenv("MINIO_HOST", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_SECURE = os.getenv("MINIO_SECURE", 0)


def check_or_create_bucket(bucket_name):
    client = get_client()

    if not client.bucket_exists(bucket_name):
        client.make_bucket(bucket_name)


def get_client():
    return Minio(
        MINIO_HOST,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=MINIO_SECURE == 1,
    )


def get_presigned_url(path):
    client = get_client()
    bucket_name = path.split("/")[0]
    object_name = "/".join(path.split("/")[1:])

    # Make the link 1 minute valid
    expires = timedelta(minutes=1)

    url = client.get_presigned_url("GET", bucket_name, object_name, expires=expires)

    return url


def list_documents(path):
    client = get_client()

    bucket_name = path.split("/")[0]
    prefix = path.split("/")[1]

    logging.info(
        f"Retrieving - path: {path}, bucket_name: {bucket_name}, prefix: {prefix}"
    )
    documents = client.list_objects(
        bucket_name=bucket_name, prefix=prefix, recursive=True
    )

    def map_document(document):
        return {
            "size": document.size,
            "filename": document.object_name.replace(f"{prefix}/", ""),
            "last_modified": document.last_modified,
            "url": f"source--custom/{document.object_name}",
        }

    def filter_documents(document):
        if "__MACOSX" in document.object_name:
            return False
        if document.is_dir:
            return False

        return True

    data = list(map(map_document, filter(filter_documents, documents)))

    # Sort on filename
    data.sort(key=lambda x: x["filename"])

    return data


def get_document(path):
    client = get_client()
    response = None

    bucket_name = path.split("/")[0]
    object_name = "/".join(path.split("/")[1:])

    logging.info(
        f"Retrieving - path: {path}, bucket_name: {bucket_name}, object_name: {object_name}"
    )
    try:
        response = client.get_object(bucket_name=bucket_name, object_name=object_name)
        doc_body = response.data
    finally:
        if response is not None:
            # Close the connection
            response.close()
            response.release_conn()

    return doc_body


def base64_to_buffer(content: str):
    import base64
    import io

    return io.BytesIO(base64.b64decode(content))


def store_buffer_in_s3(buffer, bucket_name, file_path):
    check_or_create_bucket(bucket_name)

    get_client().put_object(
        bucket_name=bucket_name,
        object_name=file_path,
        data=buffer,
        length=buffer.getbuffer().nbytes,
    )

    return f"private-artifacts/{file_path}"


def delete_document(bucket, file_path):
    return get_client().remove_object(bucket, file_path)


def delete_custom_source_bucket(custom_source):
    root_bucket_name = "source--custom"

    delete_object_list = map(
        lambda x: x.object_name,
        get_client().list_objects(root_bucket_name, custom_source[14:], recursive=True),
    )

    for delete_object in delete_object_list:
        get_client().remove_object(root_bucket_name, delete_object)
