from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional

from app.database import get_session
from app.services.llm import extract_activity_from_chat

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    location_context: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    # Proposed activity data — NOT yet saved. The client must explicitly
    # call POST /activities/ after the user confirms.
    pending_activity: Optional[dict] = None
    needs_confirmation: bool = False


@router.post("/", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    session: AsyncSession = Depends(get_session),
):
    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    result = await extract_activity_from_chat(messages, body.location_context)

    return ChatResponse(
        reply=result.reply,
        pending_activity=result.activity_data,  # None until LLM is ready to propose
        needs_confirmation=result.needs_confirmation,
    )
