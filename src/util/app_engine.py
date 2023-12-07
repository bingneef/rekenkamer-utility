import hashlib
import os
from typing import Tuple
import dotenv
import elastic_enterprise_search.exceptions
import re

from elastic_enterprise_search import AppSearch

from src.util.logger import logger

dotenv.load_dotenv()

DEFAULT_ENGINES = ["source-main"]


def _app_search_user_conn(search_api_key) -> AppSearch:
    return AppSearch(
        os.getenv("ENGINE_BASE_URL"), basic_auth=f"private-{search_api_key}"
    )


def _app_search_conn() -> AppSearch:
    return AppSearch(
        os.getenv("ENGINE_BASE_URL"),
        basic_auth=os.getenv("ENTERPRISE_SEARCH_BASIC_AUTH"),
    )


def _fetch_api_keys() -> list[dict]:
    app_search = _app_search_conn()

    # Loop
    results = []
    current_page = 1

    while True:
        api_keys = app_search.list_api_keys(current_page=current_page, page_size=250)
        results.extend(api_keys["results"])

        if len(results) >= api_keys["meta"]["page"]["total_results"]:
            break

        current_page += 1

    # Only return results that have engines
    return [
        api_key
        for api_key in results
        if "engines" in api_key.keys() and len(api_key["engines"]) > 0
    ]


def users_for_engine(engine_name: str) -> list[str]:
    api_keys = _fetch_api_keys()

    return [
        _api_key_name_to_email(api_key["name"])
        for api_key in api_keys
        if engine_name in api_key["engines"]
    ]


def verify_format_and_uniqueness_name(engine_name: str) -> tuple[bool, str]:
    app_search = _app_search_conn()
    # Check format is ok
    if not re.match(r"^[a-z0-9-]+$", engine_name):
        return (
            False,
            "ENGINE_FORMAT_ERROR",
        )

    if "--" in engine_name or engine_name[-1] == "-":
        return (
            False,
            "ENGINE_FORMAT_DASH_ERROR",
        )

    try:
        app_search.get_engine(engine_name=engine_name)
        return False, "ENGINE_ALREADY_EXISTS"
    except elastic_enterprise_search.exceptions.NotFoundError:
        return True, "ok"
    except elastic_enterprise_search.exceptions.InternalServerError:
        return False, "ENGINE_UNKNOWN_ERROR"


def remove_documents(api_key: str, engine: str, ids: list[str]):
    app_search = AppSearch(os.getenv("ENGINE_BASE_URL"), bearer_auth=api_key)

    return app_search.delete_documents(engine_name=engine, document_ids=ids)


def list_engines(api_key: str) -> list[str]:
    app_search = AppSearch(os.getenv("ENGINE_BASE_URL"), bearer_auth=api_key)

    return [engine["name"] for engine in app_search.list_engines()["results"]]


def verify_access(api_key: str, requested_engine: str) -> bool:
    engines = list_engines(api_key)

    for engine in engines:
        if engine == requested_engine:
            return True

    return False


def _email_to_api_key_name(email: str) -> str:
    hash_digest = hashlib.md5(email.encode()).hexdigest()

    # Replace all non-alphanumeric characters with a dash
    safe_email = re.sub("[^a-z0-9-]", "-", email.lower())

    return f"{safe_email}-{hash_digest}"


def _api_key_name_to_email(api_key_name: str) -> str:
    from src.models.user import User

    user = User.find_user_by_api_key_name(api_key_name)
    if user is None:
        return api_key_name

    return user.email


def api_key_for_email(email: str) -> str:
    app_search = _app_search_conn()

    api_key_name = _email_to_api_key_name(email)
    api_key = app_search.get_api_key(api_key_name=api_key_name)

    return api_key["key"]


def create_elastic_credentials(
    email: str,
) -> Tuple[str, str]:
    app_search = _app_search_conn()

    api_key_name = _email_to_api_key_name(email)

    # Check if api key already exists
    try:
        api_key = app_search.get_api_key(api_key_name=api_key_name)

        logger.info(f"Api key already existed for {email} ({api_key_name})")

        return api_key["key"], api_key_name
    except elastic_enterprise_search.exceptions.NotFoundError:
        pass

    logger.info(f"Generating new key for {email} ({api_key_name})")

    api_key = app_search.create_api_key(
        name=api_key_name,
        type="private",
        read=True,
        write=True,
        access_all_engines=False,
        engines=DEFAULT_ENGINES,
    )

    logger.info(api_key)

    return api_key["key"], api_key_name


def create_engine(engine, user_email):
    logger.info(engine)
    logger.info(user_email)
    if engine[:14] != "source-custom-":
        raise ValueError("Engine name must start with 'source-custom-'")

    app_search = _app_search_conn()
    try:
        app_search.create_engine(engine_name=engine, language="nl", type="default")
    except Exception as e:
        logger.error(e)
        raise e

    engines = update_elastic_engine_credentials(
        email=user_email, engines_to_add=[engine]
    )

    logger.info(engines)

    return {"engines": engines}


def _get_engine_list(
    engines: list[str], engines_to_add: list[str], engines_to_remove: list[str]
):
    return list(set([*engines, *engines_to_add]) - set(engines_to_remove))


def update_elastic_engine_credentials(
    email: str, engines_to_add: list[str] = [], engines_to_remove: list[str] = []
) -> list[str]:
    app_search = AppSearch(
        os.getenv("ENGINE_BASE_URL"), bearer_auth=os.getenv("ENGINE_ADMIN_API_KEY")
    )

    logger.info(os.getenv("ENGINE_ADMIN_API_KEY"))
    api_key_name = _email_to_api_key_name(email)
    logger.info(api_key_name)
    api_key = app_search.get_api_key(api_key_name=api_key_name)
    logger.info(api_key)

    engines = _get_engine_list(
        engines=api_key["engines"],
        engines_to_remove=engines_to_remove,
        engines_to_add=engines_to_add,
    )
    logger.info(engines)

    app_search.put_api_key(
        api_key_name=api_key_name,
        name=api_key_name,
        type="private",
        read=api_key["read"],
        write=api_key["write"],
        engines=engines,
    )

    return engines


def delete_engine(engine, search_api_key):
    app_search = _app_search_user_conn(search_api_key)
    app_search.delete_engine(engine_name=engine)

    return True
