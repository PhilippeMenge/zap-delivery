from datetime import datetime, timedelta

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from src.config import SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """### Hashes a password.

    Args:
        password (str): The password.

    Returns:
        str: The hashed password.
    """
    return pwd_context.hash(password)


def validate_password(password: str, hashed_password: str) -> bool:
    """### Validates a password.

    Args:
        password (str): The password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password is valid. False otherwise.
    """
    return pwd_context.verify(password, hashed_password)


def generate_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """### Generates a JWT token.

    Args:
        data (dict): The data to be encoded.
        expires_delta (timedelta, optional): The expiration time. Defaults to None.

    Returns:
        str: The JWT token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=12)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

    return encoded_jwt


def decode_token(token: str) -> dict:
    """### Decodes a JWT token.

    Args:
        token (str): The JWT token.

    Returns:
        dict: The decoded data.
    """
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except JWTError:
        return {}
    

def get_operator_email_from_token(token: str) -> str | None:
    """### Get the operator email from a JWT token.

    Args:
        token (str): The JWT token.

    Returns:
        str: The operator email.
    """
    decoded_token = decode_token(token)

    email = decoded_token.get("sub")
    
    if not isinstance(email, str):
        return None
    
    return email
