# Используем легковесный официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Запрещаем Python писать .pyc файлы и буферизовать stdout/stderr (полезно для логов)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Копируем только requirements для кеширования слоев Docker
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь остальной код проекта
COPY . .

# Создаем папку для базы данных
RUN mkdir -p /app/data

# Запускаем приложение (внутри контейнера оно будет работать на порту 8000)
CMD["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]