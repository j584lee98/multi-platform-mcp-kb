from fastapi import HTTPException, status
import bcrypt

# In-memory user store for demo purposes
users_db = {}

def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    hashed_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

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
