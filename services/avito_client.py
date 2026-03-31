import time
import asyncio
import logging
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger("avito_client")

class AvitoAPIClient:
    def __init__(self, account_id: int, client_id: str, client_secret: str):
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Базовый HTTP клиент без жестко заданного заголовка Authorization
        self._client = httpx.AsyncClient(
            base_url="https://api.avito.ru", 
            timeout=15.0
        )
        
        # Переменные для кеширования токена
        self._access_token = None
        self._token_expires_at = 0
        self._token_lock = asyncio.Lock() # Защита от race conditions при обновлении токена

    async def _ensure_token(self) -> str:
        """Проверяет валидность токена и обновляет его при необходимости."""
        async with self._token_lock:
            # Обновляем токен, если его нет или до его протухания осталось менее 60 секунд
            if not self._access_token or time.time() > self._token_expires_at - 60:
                logger.info("Запрашиваем новый access_token у Авито...")
                
                response = await self._client.post(
                    "/token/",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret
                    },
                    # httpx автоматически ставит Content-Type: application/x-www-form-urlencoded при использовании data=
                )
                response.raise_for_status()
                token_data = response.json()
                
                self._access_token = token_data["access_token"]
                # Сохраняем время протухания (текущее время + время жизни в секундах)
                self._token_expires_at = time.time() + token_data["expires_in"]
                
                logger.info("Токен Авито успешно получен и закеширован.")
                
        return self._access_token

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def get_chat_info(self, chat_id: str) -> dict:
        token = await self._ensure_token()
        response = await self._client.get(
            f"/messenger/v2/accounts/{self.account_id}/chats/{chat_id}",
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def send_message(self, chat_id: str, text: str) -> dict:
        token = await self._ensure_token()
        payload = {"message": {"text": text}, "type": "text"}
        response = await self._client.post(
            f"/messenger/v1/accounts/{self.account_id}/chats/{chat_id}/messages",
            json=payload,
            headers={"Authorization": f"Bearer {token}"}
        )
        response.raise_for_status()
        return response.json()
        
    async def close(self):
        await self._client.aclose()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def subscribe_webhook(self, webhook_url: str) -> dict:
        """Регистрирует URL для получения вебхуков от Авито."""
        token = await self._ensure_token()
        
        logger.info(f"Регистрируем webhook URL в Авито: {webhook_url}")
        response = await self._client.post(
            "/messenger/v3/webhook",
            json={"url": webhook_url},
            headers={"Authorization": f"Bearer {token}"}
        )
        
        # Если Авито вернет ошибку (например, наш сервер недоступен), скрипт упадет с понятным описанием
        response.raise_for_status() 
        return response.json()    