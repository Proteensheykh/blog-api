from datetime import datetime, timedelta, timezone
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import PyJWTError, encode, decode
from sqlalchemy.orm import Session

from . import models, utils, schemas
from .config import settings

# Secret key used for JWT encoding and decoding
SECRET_KEY = settings.secret_key
# Algorithm used for JWT encoding and decoding
ALGORITHM = settings.algorithm
# Expiration time for access tokens in minutes
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

def create_access_token(data: dict):
    """
    Create a new access token.

    Args:
        data (dict): The payload to be encoded in the token.

    Returns:
        str: The encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticate a user based on email and password.

    Args:
        db (Session): The database session.
        email (str): The user's email.
        password (str): The user's password.

    Returns:
        User: The authenticated user object if successful, False otherwise.
    """
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        return False
    if not utils.verify(password, user.password):
        return False
    return user

def verify_access_token(token: str, credentials_exception):
    """
    Verify the access token and extract the user ID.

    Args:
        token (str): The JWT token to verify.
        credentials_exception (HTTPException): The exception to raise if verification fails.

    Returns:
        TokenData: The token data containing the user ID.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    # print("token: ", token)
    try:
        payload = decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("user_id")
        expiration_time = payload.get("exp")

        # if expiration_time < datetime.utcnow().timestamp():
        #     raise HTTPException(
        #         status_code=status.HTTP_401_UNAUTHORIZED, 
        #         detail=f"Token expired please login again", 
        #         headers={"WWW-Authenticate": "Bearer"})

        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except PyJWTError:
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get the current authenticated user based on the provided token.

    Args:
        token (str): The JWT token obtained from the request.

    Returns:
        TokenData: The token data containing the user ID.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail=f"Could not validate credentials", 
        headers={"WWW-Authenticate": "Bearer"})

    
    #user = db.query(models.User).filter(models.User.id == token_data.id).first()

    return verify_access_token(token, credentials_exception)
