from pydantic import BaseModel

class File(BaseModel):
    filename: str
    filetype: str


class RandomFileName(BaseModel):
    filename: str