from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from src.auth import (
    AuthRequest,
    TokenResponse,
    create_access_token,
    get_user,
    verify_password,
)
from src.database import User, get_db
from src.logging import get_logger

router = APIRouter(tags=["Auth"])
logger = get_logger(__name__)


def _authenticate(db: Session, username: str, password: str) -> User:
    user = get_user(db, username)
    if not user or not verify_password(password, user.hashed_password):
        logger.warning("Failed login attempt", extra={"username": username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/login", response_model=TokenResponse)
@router.post("/auth/login", response_model=TokenResponse)
def login(req: AuthRequest, db: Session = Depends(get_db)):
    user = _authenticate(db, req.username, req.password)
    token = create_access_token(user.username)
    logger.info("Token issued via JSON login", extra={"username": user.username})
    return TokenResponse(access_token=token, token_type="bearer")


@router.post("/auth/token", response_model=TokenResponse)
async def login_token(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/json" in content_type:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="Username and password are required",
        )

    user = _authenticate(db, str(username), str(password))
    token = create_access_token(user.username)
    logger.info("Token issued via /auth/token", extra={"username": user.username})
    return TokenResponse(access_token=token, token_type="bearer")
