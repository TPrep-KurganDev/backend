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


class Token(BaseModel):
    access_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refreshToken: str

class AccessTokenResponse(BaseModel):
    accessToken: str
    expiresIn: int
    token_type: str

class ExamBase(BaseModel):
    title: str


class ExamCreate(ExamBase):
    pass


class ExamOut(ExamBase):
    id: int

    class Config:
        from_attributes = True

class CardBase(BaseModel):
    question: str
    answer: str


class CardCreate(CardBase):
    exam_id: int


class CardOut(CardBase):
    number: int
    exam_id: int

    class Config:
        from_attributes = True

class UserExamLink(BaseModel):
    user_id: int
    exam_id: int

    class Config:
        from_attributes = True