import os
import secrets
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
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
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 15))  # Shorter for access token
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))  # Longer for refresh token
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", 
    "http://localhost:5173,http://127.0.0.1:5173"
).split(",")  # Convert comma-separated string to list

print(f"Using ACCESS_TOKEN_EXPIRE_MINUTES: {ACCESS_TOKEN_EXPIRE_MINUTES}")
print(f"Using REFRESH_TOKEN_EXPIRE_DAYS: {REFRESH_TOKEN_EXPIRE_DAYS}")
print(f"CORS allowed origins: {CORS_ORIGINS}")

# --- Initialization ---
# Create database tables automatically if they don't exist
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Login System Assignment")

# Add CORS middleware for cookie support
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,  # Load from environment variable
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    Generates a JWT access token.
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

def create_refresh_token(user_id: int, db: Session):
    """
    Generates a refresh token and stores it in the database.
    Returns the token string.
    """
    # Generate a secure random token
    token = secrets.token_urlsafe(32)
    
    # Calculate expiration time
    expires_at = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # Store in database
    db_refresh_token = models.RefreshToken(
        user_id=user_id,
        token=token,
        expires_at=expires_at
    )
    db.add(db_refresh_token)
    db.commit()
    
    return token

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

@app.post("/api/login", response_model=schemas.TokenResponse)
def login(
    response: Response,
    user_data: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    """
    User Login Endpoint.[登录接口]
    1. Validates the email and password.
    2. Returns a JWT access token and sets refresh token in HttpOnly cookie.
    """
    # Find user by email
    user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # Verify password
    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    
    # Generate short-lived access token (15 minutes)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Generate long-lived refresh token (7 days) and store in database
    refresh_token = create_refresh_token(user.id, db)
    
    # Set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,       # Prevents JavaScript access (XSS protection)
        secure=False,        # Set to True in production with HTTPS
        samesite="lax",      # CSRF protection
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 7 days in seconds
        path="/api"          # Only send cookie for API routes
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/refresh", response_model=schemas.TokenResponse)
def refresh_access_token(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Refresh Token Endpoint.[刷新令牌接口]
    Reads refresh token from HttpOnly cookie and returns a new access token.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided"
        )
    
    # Verify refresh token exists in database and is not expired
    db_refresh_token = db.query(models.RefreshToken).filter(
        models.RefreshToken.token == refresh_token
    ).first()
    
    if not db_refresh_token:
        response.delete_cookie("refresh_token", path="/api")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )
    
    # Check if token is expired
    # Ensure both datetimes have timezone info for comparison
    now = datetime.now(timezone.utc)
    token_expires_at = db_refresh_token.expires_at
    
    # If the stored datetime is naive, make it aware (assume it's UTC)
    if token_expires_at.tzinfo is None:
        token_expires_at = token_expires_at.replace(tzinfo=timezone.utc)
    
    if now > token_expires_at:
        # Delete expired token from database
        db.delete(db_refresh_token)
        db.commit()
        response.delete_cookie("refresh_token", path="/api")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired"
        )
    
    # Get user associated with this refresh token
    user = db.query(models.User).filter(models.User.id == db_refresh_token.user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    # Generate new access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": new_access_token, "token_type": "bearer"}

@app.post("/api/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """
    Logout Endpoint.[登出接口]
    Deletes refresh token from database and clears cookie.
    """
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if refresh_token:
        # Delete refresh token from database
        db_refresh_token = db.query(models.RefreshToken).filter(
            models.RefreshToken.token == refresh_token
        ).first()
        
        if db_refresh_token:
            db.delete(db_refresh_token)
            db.commit()
    
    # Clear refresh token cookie
    response.delete_cookie("refresh_token", path="/api")
    
    return {"message": "Logged out successfully"}

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
    
    host = os.getenv("APP_HOST", "0.0.0.0")  # 默认监听所有网络接口
    port = int(os.getenv("APP_PORT", 8000))
    print(f"🚀 Starting server on {host}:{port}...")
    uvicorn.run("main:app", host=host, port=port, reload=True)