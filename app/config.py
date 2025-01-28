from pydantic import ConfigDict
from pydantic_settings import BaseSettings


class Settigns(BaseSettings):
    DB_URL: str
    SECRET: str

    model_config = ConfigDict(env_file=".env")


config = Settigns()
