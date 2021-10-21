import motor.motor_asyncio
from pymongo.database import Database
from deeprtc.common.settings import get_settings


settings = get_settings()


mongo_url = f'mongodb://{settings.mongo_username}:{settings.mongo_password}@{settings.mongo_host}:{settings.mongo_port}'


client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)

database: Database = client[settings.mongo_database]
