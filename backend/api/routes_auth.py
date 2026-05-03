from fastapi import APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends

from src.auth import create_access_token, TokenResponse
from src.config import get_settings
from src.logging import get_logger

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = get_logger(__name__)
settings = get_settings()


@router.post("/token", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    valid_username = form_data.username == settings.DEMO_USERNAME
    valid_password = form_data.password == settings.DEMO_PASSWORD

    if not (valid_username and valid_password):
        logger.warning("Failed login attempt", extra={"username": form_data.username})
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token(username=form_data.username)
    logger.info("Token issued", extra={"username": form_data.username})

    return TokenResponse(access_token=token)