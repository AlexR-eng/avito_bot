from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    avito_account_id: int
    avito_client_id: str
    avito_client_secret: str
    
    gigachat_credentials: str
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_verify_ssl: bool = False
    
    target_item_ids: str = "" 
    stub_message: str = "Здравствуйте! Я ИИ-ассистент, мои полномочия всё. Сейчас к диалогу подключится живой менеджер."
    system_prompt: str = "Ты вежливый помощник продавца на Авито. Отвечай кратко, по делу и дружелюбно."
    
    db_url: str = "sqlite+aiosqlite:///assistant.db"
    
    # Настройки сервера
    app_host: str = "127.0.0.1"
    app_port: int = 3003
    
    class Config:
        env_file = ".env"

settings = Settings()
target_items_set = {int(x.strip()) for x in settings.target_item_ids.split(",") if x.strip().isdigit()}