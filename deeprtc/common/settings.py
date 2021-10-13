from typing import Set
import nemo.collections.asr as nemo_asr
from functools import lru_cache
from pydantic import BaseSettings
from pathlib import Path
from dotenv import load_dotenv


env_location = Path().parent.parent.resolve() / '.env'

base_dir = Path().parent


load_dotenv(env_location)


class Settings(BaseSettings):
    acoustic_model_path: str
    save_folder: str

    class Config:
        env_file = env_location


@lru_cache
def get_settings():
    return Settings()


asr_model = nemo_asr.models.EncDecCTCModel.restore_from(
    restore_path=get_settings().acoustic_model_path)
