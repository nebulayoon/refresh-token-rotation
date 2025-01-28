from typing import Optional

from pydantic import BaseModel, EmailStr


class JWTTokenBase(BaseModel):
    exp: Optional[int] = None


class AccessToken(JWTTokenBase):
    sub: str
    name: str
    role: str


class RefreshToken(JWTTokenBase):
    pass


class RefreshTokenSessionData(BaseModel):
    sub: str
    name: str
    role: str
    ip: str
    device_id: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    name: str
    role: str


class RegisterDTO(BaseModel):
    name: str
    email: EmailStr
    password: str
    company: str
