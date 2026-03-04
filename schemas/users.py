from pydantic import BaseModel, Field, EmailStr


class UserRegisterSchema(BaseModel):
    name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(...)


class UserResponse(UserRegisterSchema):
    id: int = Field(...)


class UserLogin(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)
