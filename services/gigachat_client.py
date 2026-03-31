from typing import List
from tenacity import retry, stop_after_attempt, wait_exponential
from gigachat import GigaChat
from gigachat.models import Chat as GigaChatPayload, Messages, MessagesRole
from core.config import settings
from models.chat import ChatMessage

class GigaChatAdapter:
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate_reply(self, history: List[ChatMessage]) -> str:
        messages =[Messages(role=MessagesRole.SYSTEM, content=settings.system_prompt)]
        
        for msg in history:
            role = MessagesRole.USER if msg.role == "user" else MessagesRole.ASSISTANT
            messages.append(Messages(role=role, content=msg.content))
            
        payload = GigaChatPayload(messages=messages, max_tokens=250, temperature=0.7)
        
        async with GigaChat(
            credentials=settings.gigachat_credentials, 
            scope=settings.gigachat_scope,
            verify_ssl_certs=settings.gigachat_verify_ssl,
            model=settings.gigachat_model
        ) as client:
            response = await client.achat(payload)
            return response.choices[0].message.content