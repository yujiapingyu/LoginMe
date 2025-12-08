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

# 3. Token response format
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

# 4. Refresh token request format
class RefreshTokenRequest(BaseModel):
    refresh_token: str