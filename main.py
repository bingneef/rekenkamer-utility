from flask import Flask

from src.routes.api.v1.auth import api_v1_auth
from src.routes.api.v1.root import api_v1_root
from src.routes.root import root

app = Flask(__name__)
app.register_blueprint(root)
app.register_blueprint(api_v1_root)
app.register_blueprint(api_v1_auth)

if __name__ == "__main__":
    # Print all the routes
    print("Routes:")
    for rule in app.url_map.iter_rules():
        print(rule)

    # Only for debugging while developing
    app.run(host='0.0.0.0', debug=True, port=5000)
