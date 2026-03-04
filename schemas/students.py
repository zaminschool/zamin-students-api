from pydantic import BaseModel, Field


class StudentSchema(BaseModel):
    first_name: str = Field(...)
    last_name: str = Field(...)
    mark: int = Field(...)


class StudentResponse(StudentSchema):
    id: int = Field(...)
