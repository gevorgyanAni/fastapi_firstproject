from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field  # позволяет создавать схемы того, как мы должны принимать данные (в каком форрмате)
from starlette.status import HTTP_404_NOT_FOUND

app2 = FastAPI()  #создали объект от класса фаст апи
notes = []


class NoteBase(BaseModel):
    title: str = Field(default=..., min_length=3, max_length=100)
    content: str = Field(default=..., min_length=10)
    category: Optional[str] = None


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    title: Optional[str] = None
    content: Optional[str] = None
    category: Optional[str] = None


class NoteInDB(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool = False


@app2.post('/notes', response_model=NoteInDB)
def create_notes(note: NoteCreate):
    new_note = NoteInDB(
        id=len(notes) + 1,
        title=note.title,
        content=note.content,
        category=note.category,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    notes.append(new_note)
    return new_note


@app2.get('/notes/{note_id}', response_model=NoteInDB)
def get_note_by_id(note_id: int):
    note = None
    for current_note in notes:
        if current_note.id == note_id:
            note = current_note
            return note
    if not note:
        raise HTTPException(status_code=404, detail=f'Note with ID {note_id} not found')


@app2.get('/notes/find', response_model=List[NoteInDB])
def find_note(title: Optional[str] = None, content: Optional[str] = None):
    find_notes = []
    for current_note in notes:
        if title and title.lower() in current_note.title.lower() or content and content.lower() in current_note.content.lower():
            find_notes.append(current_note)

    if not find_notes:
        raise HTTPException(status_code=404, detail='Note not found')

    return find_notes


@app2.put('/notes/{note_id}', response_model=NoteInDB)
def edit_note(note_id: int, new_note: NoteUpdate):
    note = None
    for current_note in notes:
        if current_note.id == note_id:
            note = current_note
            break
    if not note:
        raise HTTPException(status_code=404, detail=f'Note with ID {note_id} not found')

    if new_note.title:
        note.title = new_note.title
    if new_note.content:
        note.content = new_note.content
    if new_note.category:
        note.category = new_note.category

    note.updated_at = datetime.now()
    return note


@app2.delete('/notes/{note_id}', response_model=dict)
def delete_note(note_id: int):
    note = None
    for note in notes:
        if note.id == note_id:
            note.is_deleted = True
            break
    if note is None:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")

    return {'message': 'Note deleted!'}


@app2.put('/notes/{note_id}/restore', response_model=NoteInDB)
def restore_note(note_id: int):
    note1 = None
    for note in notes:
        if note.id == note_id:
            note.is_deleted = False
            note.updated_at = datetime.now()
            note1 = note
            break

    if note1 is None:
        raise HTTPException(status_code=404, detail=f"Note with ID {note_id} not found")
    return note1

@app2.get('/notes', response_model=List[NoteInDB])
def get_notes(show_deleted: bool = False, category: Optional[str] = None):

    filtered_notes = [note for note in notes if (category is None or category == note.category)]

    if show_deleted:
        return filtered_notes
    else:
        filtered_notes = [note for note in filtered_notes if not note.is_deleted]
        return filtered_notes
