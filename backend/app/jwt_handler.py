from jose import jwt
from datetime import datetime, timedelta
from jose import JWTError

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"

def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
def verify_token(token):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None