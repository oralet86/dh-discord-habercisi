from dotenv import load_dotenv
import os

load_dotenv(".env")
TOKEN = os.getenv("TOKEN")
PREFIX = os.getenv("PREFIX")
TEST_CHANNEL = os.getenv("TEST_CHANNEL")
SEARCH_COOLDOWN = os.getenv("SEARCH_COOLDOWN")
DB_DIRECTORY = os.getenv("DB_DIRECTORY")