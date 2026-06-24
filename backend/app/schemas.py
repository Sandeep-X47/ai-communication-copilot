"""Pydantic schemas — the request/response contracts for every endpoint."""
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


# --- Auth --------------------------------------------------------------------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    subscription: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# --- Generation requests -----------------------------------------------------
class RewriteRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)
    tone: str = "professional"
    persona: str | None = None


class ReplyRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    mode: str = "professional"
    persona: str | None = None


class EmailRequest(BaseModel):
    purpose: str = Field(min_length=1, max_length=2000)
    tone: str = "professional"
    persona: str | None = None


class LinkedInRequest(BaseModel):
    intent: str = Field(min_length=1, max_length=2000)
    persona: str | None = None


class DatingRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    mode: str = "playful"


class GenerationResponse(BaseModel):
    input_text: str
    output_text: str
    mode: str
    tone: str
    cached: bool = False
    latency_ms: int = 0


# --- History -----------------------------------------------------------------
class HistoryItem(BaseModel):
    id: int
    input_text: str
    output_text: str
    mode: str
    tone: str
    created_at: datetime

    class Config:
        from_attributes = True
