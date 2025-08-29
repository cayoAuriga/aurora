from sqlalchemy.orm import Session
from app.repositories.syllabus_repository import SyllabusRepository

def delete_syllabus_command(db: Session, syllabus_id: int):
    try:
        syllabus = SyllabusRepository.delete(db, syllabus_id)
        if not syllabus:
            return None
        db.commit()   # ✅ Unit of Work
        return syllabus
    except Exception:
        db.rollback()
        raise
