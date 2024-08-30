from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    access_token_expire_minutes: int
    algorithm: str
    secret_key: str

    db_engine: str

    db_host: str
    db_port: str
    db_name: str
    db_user: str
    db_pass: str

    db_host_test: str
    db_port_test: str
    db_name_test: str
    db_user_test: str
    db_pass_test: str


settings = Settings()
