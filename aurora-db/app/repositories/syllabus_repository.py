from sqlalchemy.orm import Session
from app.models.syllabus_model import Syllabus
from app.schemas.syllabus_schema import SyllabusCreate

class SyllabusRepository:

    @staticmethod
    def create(db: Session, syllabus: SyllabusCreate):
        db_syllabus = Syllabus(**syllabus.dict())
        db.add(db_syllabus)
        return db_syllabus

    @staticmethod
    def get_by_subject(db: Session, subject_id: int):
        return db.query(Syllabus).filter(Syllabus.subject_id == subject_id).first()

    @staticmethod
    def delete(db: Session, syllabus_id: int):
        syllabus = db.query(Syllabus).filter(Syllabus.id == syllabus_id).first()
        if syllabus:
            db.delete(syllabus)
        return syllabus
