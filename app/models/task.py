from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.backend.db import Base

class Task(Base):
    __tablename__ = 'task'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    description = Column(String)
    status = Column(String)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'), nullable=False)

    user = relationship('User', back_populates='task')