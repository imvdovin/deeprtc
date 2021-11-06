from typing import List, Optional, Dict
from pydantic import BaseModel
from bson.objectid import ObjectId


class PyObjectId(ObjectId):

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid objectid')
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type='string')


class AudioTextTokenDto(BaseModel):
    _id: PyObjectId
    file_name: str
    text: str
    time_steps: Optional[List[Dict]]
    transcribed: bool
