from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schema import UserResponse
from auth.utils import get_current_user
from database import get_async_session
from notes.models import Note
from notes.schema import NoteResponse, NoteCreate
from notes.utils import validate_text

router = APIRouter(
    prefix="/notes",
    tags=["Notes"],
)


@router.post("/", response_model=NoteResponse)
async def create_note(
    note: NoteCreate,
    db: AsyncSession = Depends(get_async_session),
    user: UserResponse = Depends(get_current_user),
):
    try:
        corrected_text = await validate_text(note.content)
    except Exception:
        corrected_text = note.content + "_uncorrected"
    try:
        db_note = Note(title=note.title, content=corrected_text, owner_id=user.id)
        db.add(db_note)
        await db.commit()
        await db.refresh(db_note)
        return db_note
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")


@router.get("/", response_model=List[NoteResponse])
async def read_notes(
    db: AsyncSession = Depends(get_async_session),
    user: UserResponse = Depends(get_current_user),
):
    try:
        result = await db.execute(select(Note).filter_by(owner_id=user.id))
        notes = result.scalars().all()
        return notes
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail="Database error occurred")
