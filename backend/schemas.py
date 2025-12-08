from pydantic import BaseModel, EmailStr

# 1. User login/registration request format
class UserCreate(BaseModel):
    email: EmailStr  # Pydantic will automatically validate if this is a valid email format
    password: str

# 2. User information format returned to the frontend (excluding password!)
class UserOut(BaseModel):
    id: int
    email: EmailStr

    class Config:
        # Allow Pydantic to read data as ORM models
        orm_mode = True