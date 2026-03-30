from pydantic import BaseModel
from typing import Optional

class AvitoWebhookPayloadValue(BaseModel):
    chat_id: str
    author_id: int
    text: Optional[str] = None
    direction: Optional[str] = None
    type: str

class AvitoWebhookPayload(BaseModel):
    type: str
    value: AvitoWebhookPayloadValue
    
class AvitoWebhookRequest(BaseModel):
    id: str
    payload: AvitoWebhookPayload
    timestamp: int
    version: str