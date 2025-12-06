from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Config(BaseSettings):
    APP_NAME    : str = "fica-backend"
    DB_URL      : str = ""
    DB_PASSWORD : str = ""
    DB_NAME     : str = ""

config = Config()
