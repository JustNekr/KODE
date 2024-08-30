from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from auth.models import User
from auth.schema import UserCreate, UserResponse, Token
from auth.utils import (
    authenticate_user,
    create_access_token,
    get_password_hash,
)
from config import settings
from database import get_async_session


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)


@router.post("/token/", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_async_session),
):
    user = await authenticate_user(
        session,
        UserCreate(username=form_data.username, password=form_data.password),
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=int(settings.access_token_expire_minutes))
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/user/", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_async_session)):
    try:
        async with db.begin():
            result = await db.execute(select(User).filter_by(username=user.username))
            db_user = result.scalars().first()
            if db_user:
                raise HTTPException(
                    status_code=400, detail="Username already registered"
                )
            hashed_password = get_password_hash(user.password)
            db_user = User(username=user.username, hashed_password=hashed_password)
            db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
