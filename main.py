import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.database import init_db
from core.config import settings
from services.avito_client import AvitoAPIClient
from api.webhooks import router as webhooks_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Инициализация БД...")
    await init_db()
    
    # Инициализируем клиент Авито с client_id и client_secret
    app.state.avito_client = AvitoAPIClient(
        account_id=settings.avito_account_id,
        client_id=settings.avito_client_id,
        client_secret=settings.avito_client_secret
    )
    yield
    
    # Корректно закрываем соединения при остановке
    await app.state.avito_client.close()

app = FastAPI(title="Avito AI Assistant", lifespan=lifespan)

# Подключаем роутеры
app.include_router(webhooks_router, tags=["Webhooks"])

if __name__ == "__main__":
    import uvicorn
    # Запускаем на хосте и порту из настроек
    uvicorn.run("main:app", host=settings.app_host, port=settings.app_port)