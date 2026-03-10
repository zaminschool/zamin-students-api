import jwt
import time
from database import get_db
from models.user import Users
from config import get_settings
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

settings = get_settings()

security = HTTPBearer()


def encodejwt(email: str):
    payload = {
        "email": email,
        "exp": int(time.time()) + 6000
    }
    token = jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)
    return {
        "access_token": token,
        "type": "Bearer"
    }


def decodejwt(token: str):
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm]
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    payload = decodejwt(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(Users).filter(Users.email == payload.get("email")).first().__dict__
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def check_user(email, password, db):
    user = db.query(Users).filter(Users.email == email).first().__dict__
    if user is None:
        return False
    if user["password"] == password:
        return True
    return False
