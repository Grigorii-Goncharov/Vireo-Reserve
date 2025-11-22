from django.contrib.sites import requests

from config import settings


def send_telegram_message(chat_id, message):
    """Функция отправки сообщения боту в телеграм"""
    params = {
        "text": message,
        "chat_id": chat_id,
    }
    url = f"{settings.TELEGRAM_URL}{settings.TELEGRAM_TOKEN}/sendMessage"
    response = requests.post(url, params=params)
    return response
