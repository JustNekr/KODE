from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from auth.schema import UserResponse
from auth.utils import get_current_user
from database import get_async_session
from notes.models import Note
from notes.schema import NoteResponse, NoteCreate

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
    db_note = Note(title=note.title, content=note.content, owner_id=user.id)
    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)
    return db_note


@router.get("/", response_model=List[NoteResponse])
async def read_notes(
    db: AsyncSession = Depends(get_async_session),
        user: UserResponse = Depends(get_current_user)
):
    result = await db.execute(select(Note).filter_by(owner_id=user.id))
    notes = result.scalars().all()
    return notes
