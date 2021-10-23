from functools import lru_cache
from pydantic import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor


base_dir = Path(__file__).resolve().parent.parent


env_location = base_dir.parent / '.env'

media_folder = base_dir / 'media'

load_dotenv(env_location)

allowed_audio_codecs = ['wav', 'mp3']


class Settings(BaseSettings):
    model_path: str
    project_env: str
    spellchecker_url: str

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

settings = get_settings()

model_folder = base_dir.resolve() / 'models' / settings.model_path

model_folder_str = str(model_folder.resolve())

if settings.project_env != 'test':
    # asr_model = nemo_asr.models.EncDecCTCModel.restore_from(
    #     restore_path=get_settings().acoustic_model_path)
    processor = Wav2Vec2Processor.from_pretrained(
        model_folder_str)
    model = Wav2Vec2ForCTC.from_pretrained(
        model_folder_str)
