from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str
    login: str | None = None


class RefreshRequest(BaseModel):
    refreshToken: str


class AccessTokenResponse(BaseModel):
    accessToken: str
    expiresIn: int
    token_type: str
