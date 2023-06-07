from flask import Flask

from src.routes.api.v1.auth import api_v1_auth
from src.routes.api.v1.engines import api_v1_engines
from src.routes.api.v1.users import api_v1_users
from src.routes.api.v1.sources import api_v1_sources
from src.routes.api.v1.root import api_v1_root
from src.routes.api.v1.private_documents import api_v1_private_documents
from src.routes.root import root
from src.util.logger import logger


# For waitress
def create_app():
    app = Flask(__name__)
    app.register_blueprint(root)
    app.register_blueprint(api_v1_root)
    app.register_blueprint(api_v1_auth)
    app.register_blueprint(api_v1_engines)
    app.register_blueprint(api_v1_users)
    app.register_blueprint(api_v1_sources)
    app.register_blueprint(api_v1_private_documents)

    return app


if __name__ == "__main__":
    app = create_app()

    # Print all the routes
    logger.info("Routes:")
    for rule in app.url_map.iter_rules():
        logger.info(rule)

    # Only for debugging while developing
    app.run(host="0.0.0.0", debug=True, port=5000)
