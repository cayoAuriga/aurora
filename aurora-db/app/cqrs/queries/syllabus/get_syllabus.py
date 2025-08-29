from sqlalchemy.orm import Session
from app.repositories.syllabus_repository import SyllabusRepository

def get_syllabus_query(db: Session, subject_id: int):
    return SyllabusRepository.get_by_subject(db, subject_id)
