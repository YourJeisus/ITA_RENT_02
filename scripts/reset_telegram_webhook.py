#!/usr/bin/env python3
"""
Скрипт для сброса Telegram webhook и очистки pending updates
"""
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / '.env')

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN не найден")
    exit(1)

def reset_webhook():
    """Сбрасываем webhook"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook"
    params = {"drop_pending_updates": True}
    
    response = requests.post(url, params=params)
    
    if response.status_code == 200:
        print("✅ Webhook удален, pending updates очищены")
        return True
    else:
        print(f"❌ Ошибка: {response.text}")
        return False

def get_me():
    """Проверяем что бот работает"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/getMe"
    
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Бот активен: @{data['result']['username']}")
        return True
    else:
        print(f"❌ Бот не отвечает: {response.text}")
        return False

if __name__ == "__main__":
    print("🤖 Сброс Telegram webhook...")
    
    if get_me():
        if reset_webhook():
            print("🎉 Готово! Теперь можно запускать бота на Railway")
        else:
            print("❌ Не удалось сбросить webhook")
    else:
        print("❌ Проблемы с доступом к боту")
