from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from db.base import Base


class BeamMark(Base):
    __tablename__ = "beam_marks"

    beam_mark_id = Column(Integer, primary_key=True, index=True)
    beam_mark_name = Column(String(100), nullable=False)
    beam_mark_description = Column(String(1000), nullable=False, default="")
    beam_mark_status = Column(String(20), nullable=False, default="черновик")
    beam_mark_image_url = Column(String(500), nullable=True)
    beam_mark_video_url = Column(String(500), nullable=True)
    beam_mark_price = Column(Float, nullable=True)
    beam_mark_strength = Column(Float, nullable=True)
    beam_mark_created_at = Column(DateTime, default=datetime.utcnow)
    beam_mark_published_at = Column(DateTime, nullable=True)
    beam_mark_creator_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)

    creator = relationship("User", back_populates="beam_marks")
    likes = relationship("Like", back_populates="beam_mark")