from pydantic import BaseModel

class File(BaseModel):
    uuid: str
    size: int
    filetype: str
    title: str | None = None
    description: str | None = None
    filename: str | None = None
    extension: str | None = None
    owner_uuid: str | None = None


class RandomFileName(BaseModel):
    filename: str