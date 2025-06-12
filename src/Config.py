import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class TauronConfig(BaseSettings):

    username: str
    password: str = Field(secret=True)

    class Config:
        env_prefix = 'TAURON_'

class AppConfig(BaseSettings):

    working_dir: str
    checkpoint_folder: str
    storage_folder: str
    logs_folder: str

    date_format: str = '%Y-%m-%d'

    class Config:
        env_prefix = 'APP_TAURON_'


    @property
    def checkpoint_folder_path(self) -> str:
        """Returns the full path to the checkpoint folder."""
        return os.path.join(self.working_dir, self.checkpoint_folder)
        
    @property
    def storage_folder_path(self) -> str:
        """Returns the full path to the storage directory."""
        return os.path.join(self.working_dir, self.storage_folder)
        
    @property
    def logs_folder_path(self) -> str:
        """Returns the full path to the logs directory."""
        return os.path.join(self.working_dir, self.logs_folder)

    @property
    def raw_data_folder_path(self) -> str:
        return f"{self.storage_folder_path}/raw"

    def model_post_init(self, *args, **kwargs):
        """Create required directories after initialization."""
        os.makedirs(self.checkpoint_folder_path, exist_ok=True)
        os.makedirs(self.storage_folder_path, exist_ok=True)
        os.makedirs(self.logs_folder_path, exist_ok=True)


tauron_config = TauronConfig()
app_config = AppConfig()