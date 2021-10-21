from typing import Union
from pydantic import BaseModel


class CreateAudioTextTokenDto(BaseModel):
    file_name: str
    text: Union[str, None] = None
    transcribed: bool = False
