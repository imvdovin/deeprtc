from typing import Optional
from pydantic import BaseModel


class UpdateFileTextContentDto(BaseModel):
    text: str
