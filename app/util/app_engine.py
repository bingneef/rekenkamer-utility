import os

from elastic_enterprise_search import AppSearch


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
