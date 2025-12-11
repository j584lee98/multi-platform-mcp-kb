from fastapi import HTTPException, status
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory user store for demo purposes
users_db = {}

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def register_user(username: str, password: str):
    if username in users_db:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    users_db[username] = get_password_hash(password)
    return {"msg": "User registered successfully"}

def authenticate_user(username: str, password: str):
    hashed_password = users_db.get(username)
    if not hashed_password or not verify_password(password, hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {"msg": "Login successful"}
