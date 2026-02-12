from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class RegisterSchema(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=72, description="Password must be 8-72 characters long")
    full_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class VerifyOtpSchema(BaseModel):
    email: EmailStr
    otp: str = Field(..., min_length=6, max_length=6)


class UserDetailsSchema(BaseModel):
    email: EmailStr
    full_name: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    is_verified: bool
    created_at: datetime


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
