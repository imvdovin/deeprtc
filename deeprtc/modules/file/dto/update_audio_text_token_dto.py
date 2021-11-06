from typing import List, Dict, Optional
from pydantic import BaseModel


class UpdateAudioTextTokenDto(BaseModel):
    file_name: Optional[str]
    text: Optional[str]
    time_steps: Optional[List[Dict]]
    transcribed: Optional[bool]
