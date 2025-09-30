from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME:str = "GuardiumAI Registry-Catalog"
    VERSION:str = "0.0.1"
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    API_PREFIX:str = "/api"
    DATABASE_USER:str = os.getenv('DATABASE_USER', "guardu")
    DATABASE_PASSWORD:str = os.getenv('DATABASE_PASSWORD')
    DATABASE_HOST:str = os.getenv('DATABASE_HOST')
    DATABASE_PORT:int = os.getenv('DATABASE_PORT')
    DATABASE_NAME:str = os.getenv('DATABASE_NAME')
    DEBUG:bool = True
    TESTING:str = os.getenv('TESTING', "")

    db_url:str = ""
    if TESTING == "True":
        db_url = "sqlite:///:memory:"       # For unit testing only
    else:
        db_url = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"

settings = Settings()