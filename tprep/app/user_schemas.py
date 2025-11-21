from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    user_name: str


class UserCreate(UserBase):
    password: str


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
