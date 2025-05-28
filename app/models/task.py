from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.backend.db import Base


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    description = Column(String)
    status = Column(String)
    user_id = Column(
        Integer, ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    user = relationship("User", back_populates="task")
