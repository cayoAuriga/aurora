from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.cqrs.commands.syllabus.create_syllabus import create_syllabus_command
from app.cqrs.commands.syllabus.delete_syllabus import delete_syllabus_command
from app.cqrs.queries.syllabus.get_syllabus import get_syllabus_query
from app.db import get_db
from app.schemas.syllabus.syllabus_schema import SyllabusCreate, SyllabusResponse


router = APIRouter(prefix="/syllabus", tags=["syllabus"])

@router.post("/", response_model=SyllabusResponse)
def create_syllabus(syllabus: SyllabusCreate, db: Session = Depends(get_db)):
    return create_syllabus_command(db, syllabus)

@router.get("/{subject_id}", response_model=SyllabusResponse)
def get_syllabus(subject_id: int, db: Session = Depends(get_db)):
    syllabus = get_syllabus_query(db, subject_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return syllabus

@router.delete("/{syllabus_id}")
def delete_syllabus(syllabus_id: int, db: Session = Depends(get_db)):
    syllabus = delete_syllabus_command(db, syllabus_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found")
    return {"message": "Syllabus deleted"}
