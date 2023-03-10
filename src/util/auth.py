import os
import hashlib


def get_verification_code(email):
    data_string = f"{email}::{os.environ['SECRET_KEY']}"
    result_hash = hashlib.sha256(data_string.encode('ascii')).hexdigest()
    return result_hash[-8:]
