import bcrypt
import jwt
from src.config import SECRET_KEY

def hash_password(password: str) -> str:
    """### Hashes a password.
    
    Args:
        password (str): The password.

    Returns:
        str: The hashed password.
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def validate_password(password: str, hashed_password: str) -> bool:
    """### Validates a password.
    
    Args:
        password (str): The password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the password is valid. False otherwise.
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed_password)


def generate_token(email: str) -> str:
    """### Generates a JWT token.
    
    Args:
        email (str): The user's email.

    Returns:
        str: The JWT token.
    """
    return jwt.encode({"email": email}, SECRET_KEY)