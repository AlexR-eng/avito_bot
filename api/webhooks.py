from fastapi import APIRouter, Request, BackgroundTasks, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import get_db_session
from schemas.avito import AvitoWebhookRequest
from services.processor import MessageProcessorService
from services.gigachat_client import GigaChatAdapter

router = APIRouter()

@router.post("/webhook/avito")
async def avito_webhook(
    webhook_data: AvitoWebhookRequest, 
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db_session)
):
    val = webhook_data.payload.value
    
    if webhook_data.payload.type == "message" and val.type == "text" and val.direction == "in" and val.text:
        ai_client = GigaChatAdapter()
        avito_client = request.app.state.avito_client # Берем из глобального стейта (Connection Pool)
        
        processor = MessageProcessorService(db, avito_client, ai_client)
        
        background_tasks.add_task(
            processor.process_incoming_message,
            chat_id=val.chat_id,
            user_id=val.author_id,
            text=val.text
        )
        
    return {"ok": True}