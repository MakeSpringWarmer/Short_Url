from sqlmodel import SQLModel, Field
from datetime import datetime, timedelta


class URL(SQLModel, table=True):
    id: str = Field(primary_key=True)
    original_url: str = Field(max_length=2048, nullable=False)
    expiration_date: datetime = Field(nullable=False)


class URLCreate(SQLModel):
    original_url: str


class URLResponse(SQLModel):
    short_url: str
    expiration_date: datetime
    success: bool
    reason: str | None = None
