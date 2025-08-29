from sqlalchemy.orm import Session
from app.repositories.syllabus_repository import SyllabusRepository
from app.schemas.syllabus.syllabus_schema import SyllabusCreate

def create_syllabus_command(db: Session, syllabus_data: SyllabusCreate):
    try:
        syllabus = SyllabusRepository.create(db, syllabus_data)
        db.commit()   # ✅ Unit of Work
        db.refresh(syllabus)
        return syllabus
    except Exception:
        db.rollback() # rollback si falla
        raise
