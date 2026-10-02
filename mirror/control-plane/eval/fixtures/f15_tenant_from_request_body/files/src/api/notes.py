from fastapi import APIRouter, Depends, Request

from .auth import current_user
from .store import save_note

router = APIRouter()


@router.post("/notes")
async def create_note(request: Request, user=Depends(current_user)):
    body = await request.json()
    return save_note(tenant_id=body["tenant_id"], text=body["text"])
