import os
import dotenv
import elastic_enterprise_search.exceptions
import re

from elastic_enterprise_search import AppSearch

dotenv.load_dotenv()

DEFAULT_ENGINES = ["source-main"]


def list_engines(api_key: str) -> list[str]:
    app_search = AppSearch(
        os.getenv("ENGINE_BASE_URL"),
        http_auth=api_key
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
        # First 14 chars are source-custom, remaining is the requested engine
        if engine[14:] == requested_engine:
            return True

    return False


def _email_to_api_key_name(email: str) -> str:
    # Replace all non-alphanumeric characters with a dash
    return re.sub('[^a-z0-9-]', '-', email.lower())


def create_elastic_credentials(
    email: str,
) -> dict[str, str]:
    app_search = AppSearch(
        os.getenv("ENGINE_BASE_URL"),
        bearer_auth=os.getenv("ENGINE_ADMIN_API_KEY")
    )

    api_key_name = _email_to_api_key_name(email)

    # Check if api key already exists
    try:
        api_key = app_search.get_api_key(
            api_key_name=api_key_name
        )

        print(f"Api key already existed for {email} ({api_key_name})")

        return api_key['key']
    except elastic_enterprise_search.exceptions.NotFoundError:
        pass

    print(f"Generating new key for {email} ({api_key_name})")

    api_key = app_search.create_api_key(
        name=api_key_name,
        type="private",
        read=True,
        write=False,
        access_all_engines=False,
        engines=DEFAULT_ENGINES
    )

    return api_key['key']


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


if __name__ == '__main__':
    email_var = "b.steups@rekenkamer.nl"
    print(create_elastic_credentials(email_var))
    print(update_elastic_engine_credentials(email_var, engines_to_add=["source-custom-1"]))

