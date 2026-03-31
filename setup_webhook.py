import asyncio
import logging
from core.config import settings
from services.avito_client import AvitoAPIClient

logging.basicConfig(level=logging.INFO)

async def main():
    # Ваш итоговый URL, который мы настроили в Nginx
    WEBHOOK_URL = "https://assist.wizardofmoney.ru/webhook/avito"
    
    # Инициализируем клиент
    client = AvitoAPIClient(
        account_id=settings.avito_account_id,
        client_id=settings.avito_client_id,
        client_secret=settings.avito_client_secret
    )
    
    try:
        # Отправляем запрос на подписку
        result = await client.subscribe_webhook(WEBHOOK_URL)
        print("✅ Успех! Авито принял вебхук. Ответ сервера Авито:", result)
    except Exception as e:
        print("❌ Ошибка при регистрации вебхука:", str(e))
    finally:
        await client.close()

if __name__ == "__main__":
    asyncio.run(main())