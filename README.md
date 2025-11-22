# Vireo Reserve 🍽️

    Vireo Reserve - это сайт ресторан

## Описание
    **Vireo Reserve** — это бэкенд-часть SPA (Single Page Application) веб-приложения для онлайн-бронирования столов в ресторане. 
    Проект разработан на базе Django и предоставляет RESTful API для взаимодействия с фронтендом.

## ✨ Основные функции

    - Авторизация и аутентификация пользователей
    - Просмотр доступных столов в ресторане
    - Онлайн-бронирование столов с указанием даты, времени и продолжительности
    - Проверка доступности столов в реальном времени
    - Уведомления о бронировании
    - Поддержка статусов бронирований: «ожидание», «подтверждено», «отменено»

## 🛠 Технологии

    - **Backend**: Python 3.9+, Django 4.x, Django REST Framework
    - **База данных**: PostgreSQL (рекомендуется; совместим с другими СУБД, поддерживаемыми Django)

## 🚀 Установка и запуск

    git clone https://git@github.com:Grigorii-Goncharov/Vireo-Reserve.git
    cd Vireo-Reserve
   
    Создайте и активируйте виртуальное окружение:
      python -m venv venv
      source venv/bin/activate    # Linux/macOS
      # или
      venv\Scripts\activate       # Windows

    Настройте переменные окружения (создайте файл .env на основе .env.example, если он есть):
      SECRET_KEY=your_SECRET_KEY
      DEBUG=your_DEBUG
      DB_NAME=your_db_name
      DB_USER=your_db_user_name
      DB_PASSWORD=your_PASSWORD
      DB_HOST=your_host
      DB_PORT=your_port

    Выполните миграции и создайте суперпользователя:

      python manage.py migrate
      python manage.py createsuperuser

    Запустите сервер:
      python manage.py runserver 

## Лицензия 
   Этот проект распространяется по лицензии MIT.

Контакты
📧 [grigoriy85@gmail.com](mailto:grigoriy85@gmail.com)
🔗 [Grigorii-Goncharov](https://github.com/Grigorii-Goncharov)