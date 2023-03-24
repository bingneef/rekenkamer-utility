from src.models.user import User

from flask import Blueprint

api_v1_users = Blueprint('api_v1_users', __name__, url_prefix='/api/v1/users')


@api_v1_users.route('', methods=['GET'])
def list_users():
    users = User.list_users()

    return users
