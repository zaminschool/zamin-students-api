from database import get_db
from models.user import Users
from auth import get_current_user
from sqlalchemy.orm import Session
from models.student import Students
from schemas.students import StudentSchema, StudentResponse
from fastapi import Depends, HTTPException, status, APIRouter

router = APIRouter(
    prefix="/students"
)


@router.get("/", tags=["student"])
async def get_students(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    studnets = db.query(Students).where(Students.user_id == user.id).all()
    return studnets


@router.post("/", tags=["student"], dependencies=[Depends(get_current_user)], response_model=StudentResponse)
async def create_student(student: StudentSchema, db: Session = Depends(get_db),
                         current_user: Users = Depends(get_current_user)):
    user_id = current_user.id
    student_data = student.model_dump()
    new_student = Students(**student_data)
    new_student.user_id = user_id
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.put("/{student_id}", tags=["student"], response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def update_student(student_id: int, student: StudentSchema, db: Session = Depends(get_db),
                         current_user: Users = Depends(get_current_user)):
    old_student = db.query(Students).filter(Students.id == student_id).first()

    if old_student is None:
        raise HTTPException(status_code=404, detail="Student topilmadi!")

    if old_student.user_id == current_user.id:
        for key, value in student.dict().items():
            setattr(old_student, key, value)
        db.commit()
        db.refresh(old_student)
        return old_student

    raise HTTPException(status_code=404, detail="Bu sizning studentingiz emas!")


@router.delete("/{student_id}", tags=["student"], response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def delete_student(student_id: int, db: Session = Depends(get_db),
                         current_user: Users = Depends(get_current_user)):
    old_student = db.query(Students).filter(Students.id == student_id).first()

    if old_student is None:
        raise HTTPException(status_code=404, detail="Student topilmadi!")

    if old_student.user_id == current_user.id:
        db.delete(old_student)
        db.commit()
        return old_student
    raise HTTPException(status_code=404, detail="Bu sizning studentingiz emas!")
