import hashlib
import os
import dotenv
import elastic_enterprise_search.exceptions
import re

from elastic_enterprise_search import AppSearch

from src.util.logger import logger

dotenv.load_dotenv()

DEFAULT_ENGINES = ["source-main"]


def _app_search_admin_conn() -> AppSearch:
    return AppSearch(
        os.getenv("ENGINE_BASE_URL"),
        bearer_auth=os.getenv("ENGINE_ADMIN_API_KEY")
    )


def _app_search_private_conn() -> AppSearch:
    return AppSearch(
        os.getenv("ENGINE_BASE_URL"),
        bearer_auth=os.getenv("ENGINE_PRIVATE_API_KEY")
    )


def _fetch_api_keys() -> list[dict]:
    app_search = _app_search_admin_conn()

    # Loop
    results = []
    current_page = 1

    while True:
        api_keys = app_search.list_api_keys(current_page=current_page, page_size=250)
        results.extend(api_keys['results'])

        if len(results) >= api_keys['meta']['page']['total_results']:
            break

        current_page += 1

    # Only return results that have engines
    return list(
        filter(
            lambda result: 'engines' in result.keys(),
            results
        )
    )


def users_for_engine(engine_name: str) -> list[str]:
    api_keys = _fetch_api_keys()

    return list(
        map(
            lambda api_key: _api_key_name_to_email(api_key['name']),
            filter(
                lambda api_key: engine_name in api_key['engines'],
                api_keys
            )
        )
    )


def list_engines(api_key: str) -> list[str]:
    app_search = AppSearch(
        os.getenv("ENGINE_BASE_URL"),
        bearer_auth=api_key
    )

    return list(
        map(
            lambda engine: engine['name'],
            app_search.list_engines()['results']
        )
    )


def verify_access(api_key: str, requested_engine: str) -> bool:
    engines = list_engines(api_key)

    for engine in engines:
        if engine == requested_engine:
            return True

    return False


def _email_to_api_key_name(email: str) -> str:
    hash_digest = hashlib.md5(email.encode()).hexdigest()

    # Replace all non-alphanumeric characters with a dash
    safe_email = re.sub('[^a-z0-9-]', '-', email.lower())

    return f"{safe_email}-{hash_digest}"


def _api_key_name_to_email(api_key_name: str) -> str:
    from src.models.user import User

    user = User.find_user_by_api_key_hash(api_key_name)
    if user is None:
        return api_key_name

    return user.email


def api_key_for_email(email: str) -> str:
    app_search = _app_search_admin_conn()

    api_key_name = _email_to_api_key_name(email)
    api_key = app_search.get_api_key(
        api_key_name=api_key_name
    )

    return api_key['key']


def create_elastic_credentials(
    email: str,
) -> (str, str):
    app_search = _app_search_admin_conn()

    api_key_name = _email_to_api_key_name(email)

    # Check if api key already exists
    try:
        api_key = app_search.get_api_key(
            api_key_name=api_key_name
        )

        logger.info(f"Api key already existed for {email} ({api_key_name})")

        return api_key['key'], api_key_name
    except elastic_enterprise_search.exceptions.NotFoundError:
        pass

    logger.info(f"Generating new key for {email} ({api_key_name})")

    api_key = app_search.create_api_key(
        name=api_key_name,
        type="private",
        read=True,
        write=False,
        access_all_engines=False,
        engines=DEFAULT_ENGINES
    )

    return api_key['key'], api_key_name


def create_engine(engine, user_email):
    if engine[:14] != 'source-custom-':
        raise ValueError("Engine name must start with 'source-custom-'")

    app_search = _app_search_private_conn()
    app_search.create_engine(
        engine_name=engine,
        language="en",
        type='default'
    )

    engines = update_elastic_engine_credentials(
        email=user_email,
        engines_to_add=[engine]
    )

    return {
        "engines": engines
    }


def _get_engine_list(
    engines: list[str],
    engines_to_add: list[str],
    engines_to_remove: list[str]
):
    return list(set([*engines, *engines_to_add]) - set(engines_to_remove))


def update_elastic_engine_credentials(
    email: str,
    engines_to_add: list[str] = [],
    engines_to_remove: list[str] = []
) -> list[str]:
    app_search = AppSearch(
        os.getenv("ENGINE_BASE_URL"),
        bearer_auth=os.getenv("ENGINE_ADMIN_API_KEY")
    )

    api_key_name = _email_to_api_key_name(email)
    api_key = app_search.get_api_key(
        api_key_name=api_key_name
    )

    engines = _get_engine_list(
        engines=api_key['engines'],
        engines_to_remove=engines_to_remove,
        engines_to_add=engines_to_add
    )

    app_search.put_api_key(
        api_key_name=api_key_name,
        name=api_key_name,
        type="private",
        read=api_key['read'],
        write=api_key['write'],
        engines=engines
    )

    return engines


def delete_engine(engine):
    app_search = _app_search_private_conn()
    app_search.delete_engine(
        engine_name=engine
    )

    return True