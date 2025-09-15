from pydantic import BaseModel, EmailStr

class UserRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True