import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import JWTError, jwt

# Import local modules
import models
import schemas
from database import engine, get_db

load_dotenv()  # Load environment variables from .env file

# --- Configuration ---
# In a real production environment, these should be loaded from environment variables (.env).
# For this assignment, we keep them hardcoded for simplicity.
SECRET_KEY = os.getenv("SECRET_KEY", "supert_secret_key_for_interview_assignment") 
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
print(f"Using ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
# --- Initialization ---
# Create database tables automatically if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Login System Assignment")

# Password hashing context (using bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme
# This tells FastAPI that the client should send the token in the Authorization header as "Bearer <token>".
# The tokenUrl parameter is used by Swagger UI to know where to send the login request.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

# --- Utility Functions ---

def verify_password(plain_password, hashed_password):
    """Verifies if the plain password matches the hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hashes a plain password using bcrypt."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Generates a JWT token.
    Encodes the user identifier (sub) and expiration time (exp) into a string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15) # Default 15 minutes
    
    # Add expiration time to the payload
    to_encode.update({"exp": expire})
    
    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    [Dependency]
    Acts as a security guard for protected routes.
    1. Extracts the token from the Authorization header.
    2. Decodes and validates the token.
    3. Retrieves the user from the database.
    If any step fails, it raises a 401 Unauthorized error.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Decode the token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        # Check token expiration
        token_exp: int = payload.get("exp")
        # print(f"Token expiration time (exp): {token_exp}, current time: {datetime.now(timezone.utc).timestamp()}")
        if token_exp is None or datetime.now(timezone.utc) > datetime.fromtimestamp(token_exp, tz=timezone.utc):
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Check if the user exists in the database
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

# --- API Endpoints ---

@app.post("/api/register", response_model=schemas.UserOut)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    User Registration Endpoint.[注册接口]
    1. Checks if the email is already registered.
    2. Hashes the password.
    3. Saves the new user to the database.
    """
    # Check for existing user
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=400, 
            detail="Email already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    new_user = models.User(email=user.email, hashed_password=hashed_password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user

@app.post("/api/login")
def login(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    User Login Endpoint.[登录接口]
    1. Validates the email and password.
    2. Returns a JWT access token if valid.
    """
    # Find user by email
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Generate token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """
    Protected Endpoint.[受保护的端点]
    Requires a valid JWT token in the Authorization header.
    Returns the current user's information.
    """
    return current_user

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("APP_PORT", 8000))
    print(f"🚀 Starting server on port {port}...")
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)