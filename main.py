import uvicorn
from models.user import Users
from config import get_settings
from sqlalchemy.orm import Session
from models.student import Students
from database import engine, get_db
from fastapi.middleware.cors import CORSMiddleware
from schemas.students import StudentSchema, StudentResponse
from fastapi import FastAPI, Depends, HTTPException, Body, status
from auth import encodejwt, check_user, get_current_user
from schemas.users import UserRegisterSchema, UserResponse, UserLogin

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    Users.metadata.create_all(bind=engine)


@app.get("/user/me", tags=["user"])
async def get_users(current_user: Users = Depends(get_current_user)):
    return {"data": current_user}


@app.post("/users", tags=["user"], response_model=UserResponse)
async def create_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    new_user = Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/login", tags=["user"])  # login
async def login_user(user: UserLogin = Body(...), db: Session = Depends(get_db)):
    if check_user(user.email, user.password, db):
        return encodejwt(user.email)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")


@app.get("/students", tags=["student"])
async def get_students(user: Users = Depends(get_current_user), db: Session = Depends(get_db)):
    studnets = db.query(Students).where(Students.user_id == user["id"]).all()
    return studnets



@app.post("/students", tags=["student"], dependencies=[Depends(get_current_user)], response_model=StudentResponse)
async def create_student(student: StudentSchema, db: Session = Depends(get_db),
                         current_user: Users = Depends(get_current_user)):
    user_id = current_user['id']
    student_data = student.model_dump()
    new_student = Students(**student_data)
    new_student.user_id = user_id
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student

@app.put("/students/{student_id}", tags=["student"], response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def update_student(student_id: int, student: StudentSchema, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    old_student = db.query(Students).filter(Students.id == student_id).first()

    if old_student is None:
        raise HTTPException(status_code=404, detail="Student topilmadi!")

    if old_student.user_id == current_user["id"]:
        for key, value in student.dict().items():
            setattr(old_student, key, value)
        db.commit()
        db.refresh(old_student)
        return old_student

    raise HTTPException(status_code=404, detail="Bu sizning studentingiz emas!")



@app.delete("/students/{student_id}", tags=["student"], response_model=StudentResponse, status_code=status.HTTP_200_OK)
async def delete_student(student_id: int, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    old_student = db.query(Students).filter(Students.id == student_id).first()

    if old_student is None:
        raise HTTPException(status_code=404, detail="Student topilmadi!")

    if old_student.user_id == current_user["id"]:
        db.delete(old_student)
        db.commit()
        return old_student
    raise HTTPException(status_code=404, detail="Bu sizning studentingiz emas!")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
