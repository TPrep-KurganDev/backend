from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refreshToken: str

class AccessTokenResponse(BaseModel):
    accessToken: str
    expiresIn: int
    token_type: str


