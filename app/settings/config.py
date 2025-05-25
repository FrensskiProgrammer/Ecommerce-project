from os import getenv
from dotenv import load_dotenv

load_dotenv()

class Settings:

    def __init__(self):
        self.database_host = getenv('DATABASE_HOST')
        self.database_port = getenv('DATABASE_PORT')
        self.database_user = getenv('DATABASE_USER')
        self.database_password = getenv('DATABASE_PASSWORD')
        self.database_name = getenv('DATABASE_NAME')

        self.secret_key = getenv('SECRET_KEY')
        self.algorithm = getenv('ALGORITHM')

settings = Settings()