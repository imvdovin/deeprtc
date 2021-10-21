from functools import lru_cache
from pydantic import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor


env_location = Path(__file__).resolve().parent.parent.parent / '.env'

base_dir = Path().parent


load_dotenv(env_location)


class Settings(BaseSettings):
    acoustic_model_path: str
    save_folder: str
    project_env: str

    mongo_username: str
    mongo_password: str
    mongo_database: str
    mongo_host: str
    mongo_port: int

    class Config:
        env_file = env_location


@lru_cache
def get_settings():
    return Settings()


model = None
processor = None

gpu_usage = 'cuda:0'

if Settings().project_env != 'test':
    # asr_model = nemo_asr.models.EncDecCTCModel.restore_from(
    #     restore_path=get_settings().acoustic_model_path)
    processor = Wav2Vec2Processor.from_pretrained(
        "anton-l/wav2vec2-large-xlsr-53-russian")
    model = Wav2Vec2ForCTC.from_pretrained(
        "anton-l/wav2vec2-large-xlsr-53-russian")
