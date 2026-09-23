from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship

from db.base import Base


class Like(Base):
    __tablename__ = "likes"

    like_id = Column(Integer, primary_key=True, index=True)
    like_user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    like_beam_mark_id = Column(
        Integer, ForeignKey("beam_marks.beam_mark_id"), nullable=False
    )

    user = relationship("User", back_populates="likes")
    beam_mark = relationship("BeamMark", back_populates="likes")
