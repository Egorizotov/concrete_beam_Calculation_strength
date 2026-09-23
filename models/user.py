from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from db.base import Base


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_username = Column(String(50), nullable=False, unique=True)
    user_email = Column(String(100), nullable=False, unique=True)

    likes = relationship("Like", back_populates="user")
    beam_marks = relationship("BeamMark", back_populates="creator")