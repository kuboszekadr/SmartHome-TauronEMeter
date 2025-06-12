import yaml

from pydantic import BaseModel, Field
from src.Config import app_config

from typing import Optional
import datetime as dt

class Checkpoint(BaseModel):
    name: str
    last_date: Optional[dt.datetime] = Field(default=dt.datetime(year=2025, month=1, day=1), 
                                             description="Last processed date in YYYY-MM-DD format"
                                             )

    @property
    def path(self) -> str:
        return f"{app_config.checkpoint_folder_path}/{self.name}.yaml"

    def dump(self) -> None:
        with open(self.path, 'w', encoding='UTF-8') as f:
            yaml.dump(self.model_dump(), f)

    def load(self) -> None:
        try:
            with open(self.path, 'r', encoding='UTF-8') as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                self.model_validate(data)
        except FileNotFoundError:
            pass
        except yaml.YAMLError as e:
            raise ValueError(f"Error loading checkpoint file: {e}")
