import os
import base64
from cryptography.fernet import Fernet
import dotenv

dotenv.load_dotenv()


fernet = Fernet(base64.urlsafe_b64encode(os.environ["SECRET_KEY"].encode("ascii")))
