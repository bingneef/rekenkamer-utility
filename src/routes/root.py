from flask import Blueprint

root = Blueprint('root', __name__, url_prefix='/')


@root.route('/')
def landing():
    return "Welcome to the utility API"


@root.route('/healthcheck')
def healthcheck():
    return {
        'status': 'ok'
    }
