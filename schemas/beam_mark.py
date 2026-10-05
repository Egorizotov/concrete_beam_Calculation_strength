from datetime import datetime
from pydantic import BaseModel, Field


class BeamMarkResponse(BaseModel):
    beam_mark_id: int
    beam_mark_name: str
    beam_mark_description: str | None
    beam_mark_status: str
    beam_mark_image_url: str | None
    beam_mark_video_url: str | None
    beam_mark_price: float | None
    beam_mark_strength: float | None
    beam_mark_created_at: datetime
    beam_mark_published_at: datetime | None
    is_mine: bool = False
    is_liked: bool = False

    class Config:
        from_attributes = True


class BeamMarkCreate(BaseModel):
    beam_mark_name: str = Field(..., min_length=1, max_length=100)
    beam_mark_description: str = Field(default="", max_length=1000)
    beam_mark_price: float = Field(..., ge=0)
    beam_mark_strength: float = Field(..., ge=0)


class BeamMarkPublish(BaseModel):
    beam_mark_description: str = Field(..., min_length=1, max_length=1000)
    beam_mark_price: float = Field(..., ge=0)
    beam_mark_strength: float = Field(..., ge=0)


class LikeRequest(BaseModel):
    value: int = Field(..., ge=0, le=1)  # 0 или 1