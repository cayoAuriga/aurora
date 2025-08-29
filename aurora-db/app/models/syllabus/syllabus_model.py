from sqlalchemy import Column, Integer, String, ForeignKey
from app.db import Base

class Syllabus(Base):
    __tablename__ = "syllabus"

    id = Column(Integer, primary_key=True, autoincrement=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), unique=True, nullable=False)
    file_url = Column(String(255))
