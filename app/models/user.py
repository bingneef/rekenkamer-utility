import os
import base64
from datetime import datetime, timedelta

from app.util.db import get_conn
from dataclasses import dataclass, asdict
import bcrypt
from cryptography.fernet import Fernet

table_name = "users"

fernet = Fernet(base64.urlsafe_b64encode(os.environ['SECRET_KEY'].encode('ascii')))


@dataclass
class User:
    display_name: str
    email: str
    password: str = None
    search_api_key: str = None
    password_hash: str = None
    salt: str = None
    search_api_key_hash: str = None
    _id: str = None
    db_conn = get_conn()

    def set_password_hash(self, password: str):
        self.salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('ascii'), self.salt)

    def set_search_api_key(self, search_api_key: str):
        self.search_api_key_hash = fernet.encrypt(f"{self.email}::{search_api_key}".encode('ascii'))

    @staticmethod
    def find_user(email: str) -> 'User':
        user = get_conn()[table_name].find_one({'email': email})
        if user is None:
            return None

        return User(**user)

    @staticmethod
    def find_user_by_api_key_hash(search_api_key_hash: str) -> 'User':
        user = get_conn()[table_name].find_one({'search_api_key_hash': search_api_key_hash})
        if user is None:
            return None

        return User(**user)

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode('ascii'), self.password_hash)

    @property
    def search_api_key_fmt(self) -> str:
        email, api_key = fernet.decrypt(self.search_api_key_hash).decode('ascii').split('::')
        if email != self.email:
            raise Exception("Invalid email")

        return api_key

    @property
    def document_access_token(self) -> str:
        timestamp = datetime.now() + timedelta(days=1)
        data = f"{timestamp.timestamp()}::{self.search_api_key_fmt}"
        return fernet.encrypt(data.encode('ascii')).decode('ascii')

    @staticmethod
    def decode_document_access_token(token: str) -> str:
        timestamp, api_key = fernet.decrypt(token.encode('ascii')).decode('ascii').split('::')
        if datetime.fromtimestamp(float(timestamp)) < datetime.now():
            raise Exception("Token expired")

        return api_key

    def persist(self):
        self.db_conn[table_name].update_one(
            {'email': self.email},
            {'$set': self.clean_dict},
            upsert=True
        )

    @property
    def clean_dict(self):
        data = asdict(self)

        # Exclude _id from the data
        data.pop('_id')

        # Exclude password from the data
        data.pop('password')

        # Exclude search_api_key from the data
        data.pop('search_api_key')

        return data

    def __post_init__(self):
        if self.password is not None:
            self.set_password_hash(self.password)
            self.password = None

        if self.search_api_key is not None:
            self.set_search_api_key(self.search_api_key)
            self.search_api_key = None
