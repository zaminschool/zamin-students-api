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


@app.get("/students", tags=["student"], dependencies=[Depends(get_current_user)])
async def get_students(db: Session = Depends(get_db)):
    return db.query(Students).all()


@app.post("/students", tags=["student"], dependencies=[Depends(get_current_user)], response_model=StudentResponse)
async def create_student(student: StudentSchema, db: Session = Depends(get_db), current_user: Users = Depends(get_current_user)):
    user_id = current_user['id']
    student_data = student.model_dump()
    new_student = Students(**student_data)
    new_student.user_id = user_id
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
