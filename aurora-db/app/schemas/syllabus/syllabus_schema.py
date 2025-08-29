from pydantic import BaseModel

class SyllabusBase(BaseModel):
    subject_id: int
    file_url: str

class SyllabusCreate(SyllabusBase):
    pass

class SyllabusResponse(SyllabusBase):
    id: int

    class Config:
        orm_mode = True
