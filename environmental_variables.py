from dotenv import load_dotenv
import os

load_dotenv(".env")
TOKEN = str(os.getenv("TOKEN", ""))
assert TOKEN != "", "TOKEN is not set in .env"

PREFIX = str(os.getenv("PREFIX", ""))
assert PREFIX != "", "PREFIX is not set in .env"

DB_DIRECTORY = str(os.getenv("DB_DIRECTORY", ""))
assert DB_DIRECTORY != "", "DB_DIRECTORY is not set in .env"

DH_DOMAIN = str(os.getenv("DH_DOMAIN", ""))
assert DH_DOMAIN != "", "DH_DOMAIN is not set in .env"

TEST_CHANNEL = int(os.getenv("TEST_CHANNEL", -1))
assert TEST_CHANNEL != -1, "TEST_CHANNEL is not set in .env"

SEARCH_COOLDOWN = int(os.getenv("SEARCH_COOLDOWN", -1))
assert SEARCH_COOLDOWN != -1, "SEARCH_COOLDOWN is not set in .env"