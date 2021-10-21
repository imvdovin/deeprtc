from functools import lru_cache
from pymongo.results import InsertOneResult, UpdateResult
from pymongo.collection import Collection
from deeprtc.common.db import database
from deeprtc.modules.file.dto.create_audio_text_token_dto import CreateAudioTextTokenDto
from deeprtc.modules.file.dto.update_audio_text_token_dto import UpdateAudioTextTokenDto
from deeprtc.modules.file.dto.audio_text_token_dto import AudioTextTokenDto
from bson.objectid import ObjectId


@lru_cache()
def get_audio_texts_collection() -> Collection:
    return database.get_collection(
        'audio_texts')


class FileRepository:
    collection: Collection = get_audio_texts_collection()

    async def create(self, create_dto: CreateAudioTextTokenDto):
        res: InsertOneResult = await self.collection.insert_one(create_dto.dict())

        return res

    async def update(self, filter, update_dto: UpdateAudioTextTokenDto):
        res: UpdateResult = await self.collection.update_one(filter, {'$set': update_dto.dict(exclude_none=True)})

        return res

    async def find_one(self, object_id):
        res: AudioTextTokenDto = await self.collection.find_one({'_id': ObjectId(object_id)})

        return res
