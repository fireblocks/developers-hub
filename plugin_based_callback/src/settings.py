import os
import logging
from src import helpers
from dotenv import load_dotenv
from src.databases.mongo import MongoDB
from src.databases.postgres import PostgresDB

logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Map db type to db class name
DB_CLASS_MAP = {
    "postgres": PostgresDB,
    "mongodb": MongoDB,
}

PLUGINS = helpers.load_plugin_list(os.getenv("PLUGINS"))
DB_TYPE = os.getenv("DB_TYPE")  # postgres/mongo

# For TxID Validation Plugin
DB_TABLE = os.getenv("DB_TABLE")

DB_COLUMN = os.getenv("DB_COLUMN")
DB_USER = os.getenv("DB_USER")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
COSIGNER_PUBLIC_KEY_PATH = os.getenv("COSIGNER_PUBLIC_KEY_PATH")
CALLBACK_PRIVATE_KEY_PATH = os.getenv("CALLBACK_PRIVATE_KEY_PATH")
EXTRA_SIGNATURE_PUBLIC_KEY_PATH = os.getenv("EXTRA_SIGNATURE_PUBLIC_KEY_PATH")
SERVER_PORT = int(os.getenv("APP_LISTENING_PORT", 8000))
FIREBLOCKS_API_KEY = os.getenv("FIREBLOCKS_API_KEY")
FIREBLOCKS_API_PRIVATE_KEY_PATH = os.getenv("FIREBLOCKS_API_PRIVATE_KEY_PATH")
FIREBLOCKS_API_SECRET = open(FIREBLOCKS_API_PRIVATE_KEY_PATH, 'r').read() if FIREBLOCKS_API_PRIVATE_KEY_PATH else None


DB_CONFIG = {
    "user": DB_USER,
    "host": DB_HOST,
    "password": DB_PASSWORD,
    "port": DB_PORT,
    "database": DB_NAME,
}




