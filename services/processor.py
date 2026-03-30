import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.config import settings, target_items_set
from models.chat import ChatSession, ChatMessage
from services.avito_client import AvitoAPIClient
from services.gigachat_client import GigaChatAdapter

logger = logging.getLogger("processor")

class MessageProcessorService:
    def __init__(self, db: AsyncSession, avito_client: AvitoAPIClient, ai_client: GigaChatAdapter):
        self.db = db
        self.avito = avito_client
        self.ai = ai_client

    async def process_incoming_message(self, chat_id: str, user_id: int, text: str):
        try:
            # 1. Получаем/создаем сессию
            result = await self.db.execute(select(ChatSession).where(ChatSession.chat_id == chat_id))
            session = result.scalars().first()

            if not session:
                chat_info = await self.avito.get_chat_info(chat_id)
                context = chat_info.get("context", {})
                item_id = context.get("value", {}).get("id") if context.get("type") == "item" else None

                if not item_id or (target_items_set and item_id not in target_items_set):
                    return # Игнорируем нецелевые объявления

                session = ChatSession(chat_id=chat_id, item_id=item_id)
                self.db.add(session)
                await self.db.commit()

            # 2. Проверка лимитов
            if session.is_operator_connected:
                return

            if session.ai_reply_count >= 5:
                await self._send_stub_and_disconnect(session)
                return

            # 3. Сохраняем сообщение юзера
            self.db.add(ChatMessage(chat_id=chat_id, role="user", content=text))
            await self.db.commit()

            # 4. Получаем историю
            history_result = await self.db.execute(
                select(ChatMessage).where(ChatMessage.chat_id == chat_id).order_by(ChatMessage.id.asc())
            )
            history = history_result.scalars().all()

            # 5. Генерируем и отправляем ответ
            ai_text = await self.ai.generate_reply(history)
            await self.avito.send_message(chat_id=chat_id, text=ai_text)

            # 6. Сохраняем ответ ИИ
            self.db.add(ChatMessage(chat_id=chat_id, role="assistant", content=ai_text))
            session.ai_reply_count += 1
            await self.db.commit()

        except Exception as e:
            logger.error(f"Ошибка в чате {chat_id}: {str(e)}", exc_info=True)
            await self.db.rollback()

    async def _send_stub_and_disconnect(self, session: ChatSession):
        try:
            await self.avito.send_message(chat_id=session.chat_id, text=settings.stub_message)
            session.is_operator_connected = True
            await self.db.commit()
        except Exception as e:
            logger.error(f"Ошибка отправки заглушки: {str(e)}")