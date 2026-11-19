from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional

class CreateUrlRequest(BaseModel):
    original_url: HttpUrl
    custom_alias: Optional[str] = Field(default=None, min_length=3, max_length=20,
                                        pattern=r"^[A-Za-z0-9_-]+$")
    expires_at: Optional[datetime] = None

class UrlResponse(BaseModel):
    short_code: str
    short_url: str
    original_url: str
    created_at: datetime
    expires_at: Optional[datetime] = None

class AnalyticsResponse(BaseModel):
    short_code: str
    click_count: int
