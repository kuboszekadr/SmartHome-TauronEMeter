from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class TauronConfig(BaseSettings):

    username: str
    password: str = Field(secret=True)

    class Config:
        env_prefix = 'TAURON_'

class AppConfig(BaseSettings):
    checkpoint_folder: str
    storage_path: str
    logs_folder: str

    date_format: str = '%Y-%m-%d'

    class Config:
        env_prefix = 'APP_TAURON_'

    @property
    def raw_data_folder(self) -> str:
        return f"{self.storage_path}/raw"



tauron_config = TauronConfig()
app_config = AppConfig()