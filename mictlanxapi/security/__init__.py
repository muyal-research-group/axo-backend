import bcrypt
from datetime import datetime, timedelta, timezone
import jwt

async def hash_value(value: str) -> str:
    # Generate salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(value.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')  # Convert bytes to string for storage

async def verify_password(stored_value: str, provided_value: str) -> bool:
    return bcrypt.checkpw(provided_value.encode('utf-8'), stored_value.encode('utf-8'))

def create_access_token(SECRET_KEY:str,ALGORITHM:str,data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt