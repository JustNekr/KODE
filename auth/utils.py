from datetime import datetime, timedelta
from typing import Annotated, Optional, Union

from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.models import User
from auth.schema import UserResponse, UserCreate

from database import get_async_session
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=int(settings.access_token_expire_minutes)
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def authenticate_user(
    session: AsyncSession, data: UserCreate
) -> Union[UserResponse, bool]:
    try:
        result = await session.execute(select(User).filter_by(username=data.username))
        user: UserResponse = result.scalars().first()
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
    if not user:
        return False
    if not verify_password(data.password, user.hashed_password):
        return False
    return user


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_async_session),
) -> Union[UserResponse, HTTPException]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    try:
        result = await session.execute(select(User).filter_by(id=user_id))
        user: UserResponse = result.scalars().first()
        if user is None:
            raise credentials_exception
        return user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
