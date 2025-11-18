FROM python:3.13-slim

# Установка системных зависимостей, включая curl для скачивания скрипта
RUN apt-get update && apt-get install -y --no-install-recommends \
    gettext \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /Vireo_Reserve

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry

# Копируем файлы зависимостей
COPY pyproject.toml poetry.lock ./

# Настраиваем Poetry и устанавливаем зависимости
# --no-root: не устанавливаем сам проект как пакет (опционально, но безопасно)
RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-root

# Копируем исходный код
COPY . .

# Создаём папку media (на случай, если том не смонтирован)
RUN mkdir -p /Vireo_Reserve/media

# Открываем порт (для документации, не обязателен)
EXPOSE 8000

# Запуск приложения
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
