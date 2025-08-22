from pydantic import BaseModel

class SkillBase(BaseModel):
    name: str

class SkillCreate(SkillBase):
    pass

class SkillOut(SkillBase):
    id: int
    class Config:
        from_attributes = True
