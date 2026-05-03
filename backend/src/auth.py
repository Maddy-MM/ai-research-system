from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from src.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str


# ---------------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------------

def create_access_token(username: str) -> str:
    """
    Creates a signed JWT token.

    Payload fields:
      sub  — "subject", standard JWT claim, holds the username
      exp  — expiry timestamp, jose validates this automatically on decode
      iat  — issued-at timestamp, useful for auditing
    """
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_EXPIRY_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> TokenData:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return TokenData(username=username)
    except JWTError:
        raise credentials_exception


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

# OAuth2PasswordBearer extracts the Bearer token from the Authorization header
# and points Swagger docs to the login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenData:
    return verify_token(token)