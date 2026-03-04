**production-ready FastAPI + JWT + Password Hashing** arxitekturasi

Bu versiyada mavjud:

* Parol `bcrypt` bilan hash qilinadi
* JWT `exp` claim ishlatiladi
* `.env` orqali SECRET
* Access token (30 min)
* Proper error handling
* Dependency orqali current user olish
* Clean structure

---

# Papka Strukturasi

```
app/
 ├── main.py
 ├── config.py
 ├── database.py
 ├── models.py
 ├── schemas.py
 ├── auth.py
 ├── routes.py
.env
requirements.txt
```

---

# 1. requirements.txt

```
fastapi
uvicorn
python-jose
passlib[bcrypt]
python-dotenv
sqlalchemy
```

---

# 2. .env

```
JWT_SECRET=super_secret_key_12345
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

# 3. config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
```

---

# 4. database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./blog.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

---

# 5. models.py

```python
from sqlalchemy import Column, Integer, String
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    email = Column(String, unique=True, index=True)
    password = Column(String, nullable=False)


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
```

---

# 6. schemas.py

```python
from pydantic import BaseModel, EmailStr, Field


class PostCreate(BaseModel):
    title: str
    content: str


class PostResponse(PostCreate):
    id: int

    class Config:
        orm_mode = True


class UserCreate(BaseModel):
    fullname: str
    email: EmailStr
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str
```

---

# 7. auth.py

```python
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database import SessionLocal
from models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = decode_token(token)

    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == payload.get("sub")).first()

    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user
```

---

# 8. routes.py

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import Base, engine
from models import User, Post
from schemas import UserCreate, UserLogin, PostCreate, PostResponse
from auth import (
    get_db,
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)

router = APIRouter()

Base.metadata.create_all(bind=engine)


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)

    new_user = User(
        fullname=user.fullname,
        email=user.email,
        password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_access_token({"sub": new_user.email})

    return {
        "access_token": token,
        "token_type": "Bearer"
    }


@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({"sub": db_user.email})

    return {
        "access_token": token,
        "token_type": "Bearer"
    }


@router.post("/posts", response_model=PostResponse)
def create_post(
        post: PostCreate,
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_post = Post(title=post.title, content=post.content)

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


@router.get("/posts", response_model=list[PostResponse])
def get_posts(
        db: Session = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    return db.query(Post).all()
```

---

# 9. main.py

```python
from fastapi import FastAPI
from routes import router

app = FastAPI(title="Production Blog API")

app.include_router(router)
```

---

# Ishga tushirish

```
uvicorn app.main:app --reload
```

---

# Endi Bizda Bor

* Professional JWT
* Password hashing
* SQLite DB
* Proper validation
* Clean architecture
* Protected routes
* Token expiration
* Secure secret

---

keyingi bosqichda:

* Refresh token
* Role-based access
* Dockerfile
* PostgreSQL
* Alembic migration
* Swagger customization

qilishimiz mumkin.
