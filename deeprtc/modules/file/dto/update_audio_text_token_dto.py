from typing import Optional
from pydantic import BaseModel


class UpdateAudioTextTokenDto(BaseModel):
    file_name: Optional[str]
    text: Optional[str]
    transcribed: Optional[bool]
