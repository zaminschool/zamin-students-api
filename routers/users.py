from database import get_db
from models.user import Users
from sqlalchemy.orm import Session
from auth import encodejwt, check_user, get_current_user
from fastapi import Depends, HTTPException, Body, status, APIRouter
from schemas.users import UserRegisterSchema, UserResponse, UserLogin

router = APIRouter(
    prefix="/users"
)


@router.get("/me", tags=["user"])
async def get_users(current_user: Users = Depends(get_current_user)):
    return {"data": current_user}


@router.post("/register", tags=["user"], response_model=UserResponse)
async def create_user(user: UserRegisterSchema, db: Session = Depends(get_db)):
    new_user = Users(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", tags=["user"])  # login
async def login_user(user: UserLogin = Body(...), db: Session = Depends(get_db)):
    if check_user(user.email, user.password, db):
        return encodejwt(user.email)
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
