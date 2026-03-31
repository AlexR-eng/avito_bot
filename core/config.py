import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    avito_account_id: int
    avito_client_id: str
    avito_client_secret: str
    
    gigachat_credentials: str
    gigachat_scope: str = "GIGACHAT_API_PERS"
    gigachat_verify_ssl: bool = False
    gigachat_model: str = "GigaChat-2"

    target_item_ids: str = "" 
    stub_message: str = "Здравствуйте! Я ИИ-ассистент, мои полномочия всё. Сейчас к диалогу подключится живой менеджер."
    prompt_file_path: str = "prompts/system_prompt.md"

    db_url: str = "sqlite+aiosqlite:///data/assistant.db"
    
    # Метод для получения текста промпта из файла
    def get_system_prompt(self) -> str:
        path = Path(self.prompt_file_path)
        if path.exists():
            try:
                return path.read_text(encoding="utf-8")
            except Exception as e:
                print(f"Ошибка чтения файла промпта: {e}")
        
        # Запасной промпт, если файл не найден
        return "Ты вежливый ассистент на Авито."


    
    # Настройки сервера
    app_host: str = "127.0.0.1"
    app_port: int = 3003
    
    class Config:
        env_file = ".env"

settings = Settings()
target_items_set = {int(x.strip()) for x in settings.target_item_ids.split(",") if x.strip().isdigit()}