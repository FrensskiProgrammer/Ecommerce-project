import os

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


class Settings:
    """Класс для безопасного хранения данных"""

    database_host = os.getenv("DATABASE_HOST")
    database_port = int(os.getenv("DATABASE_PORT"))
    database_user = os.getenv("DATABASE_USER")
    database_password = os.getenv("DATABASE_PASSWORD")
    database_name = os.getenv("DATABASE_NAME")

    secret_key = os.getenv("SECRET_KEY")
    algorithm = os.getenv("ALGORITHM")
