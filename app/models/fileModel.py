from pydantic import BaseModel

class File(BaseModel):
    uuid: str
    filename: str | None = None
    size: int
    filetype: str
    extension: str | None = None
    owner_uuid: str | None = None


class RandomFileName(BaseModel):
    filename: str