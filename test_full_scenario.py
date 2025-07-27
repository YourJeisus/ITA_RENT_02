#!/usr/bin/env python3
"""
🧪 ПОЛНОЕ ТЕСТИРОВАНИЕ СЦЕНАРИЯ ITA_RENT_BOT

Этапы тестирования:
1. Обновление пользователя до Premium
2. Настройка частоты уведомлений на 2 минуты  
3. Запуск скрапера для получения новых объявлений
4. Проверка отправки уведомлений в Telegram
"""
import sys
import os
import time
import asyncio
import subprocess
from pathlib import Path
from datetime import datetime

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

def print_step(step_num: int, description: str):
    """Печатает красивый заголовок этапа"""
    print("\n" + "="*60)
    print(f"🔄 ЭТАП {step_num}: {description}")
    print("="*60)

def run_command(command: str, description: str = "") -> bool:
    """Выполняет команду и возвращает результат"""
    if description:
        print(f"⚡ {description}")
    
    print(f"💻 Выполняем: {command}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            timeout=300  # 5 минут таймаут
        )
        
        if result.returncode == 0:
            print(f"✅ Команда выполнена успешно")
            if result.stdout:
                print(f"📝 Вывод:\n{result.stdout}")
            return True
        else:
            print(f"❌ Ошибка выполнения команды (код: {result.returncode})")
            if result.stderr:
                print(f"🚨 Ошибка:\n{result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ Таймаут выполнения команды (300 секунд)")
        return False
    except Exception as e:
        print(f"❌ Исключение при выполнении команды: {e}")
        return False

def update_user_to_premium():
    """Этап 1: Обновление пользователя до Premium"""
    print_step(1, "ОБНОВЛЕНИЕ ПОЛЬЗОВАТЕЛЯ ДО PREMIUM")
    
    # Запускаем локальный скрипт обновления
    return run_command(
        "python update_user_to_premium.py",
        "Обновляем Your@jeisus.ru до Premium статуса"
    )

def update_railway_variables():
    """Этап 2: Настройка переменных Railway"""
    print_step(2, "НАСТРОЙКА ПЕРЕМЕННЫХ RAILWAY")
    
    variables = {
        "DEBUG_NOTIFICATIONS": "true",
        "NOTIFICATION_INTERVAL_SECONDS": "120"  # 2 минуты
    }
    
    success = True
    for var_name, var_value in variables.items():
        success &= run_command(
            f"railway variables set {var_name}={var_value}",
            f"Устанавливаем {var_name}={var_value}"
        )
    
    return success

def trigger_scraper():
    """Этап 3: Запуск скрапера через Railway"""
    print_step(3, "ЗАПУСК СКРАПЕРА")
    
    # Попробуем несколько способов запуска скрапера
    commands = [
        ("railway run python src/parsers/run_scraping.py", "Прямой запуск скрапера"),
        ("railway run python cron_scraper.py", "Запуск через cron_scraper"),
    ]
    
    for command, description in commands:
        print(f"\n🔄 Попытка: {description}")
        if run_command(command, description):
            print("✅ Скрапер запущен успешно!")
            return True
        print("⚠️ Попытка не удалась, пробуем следующую...")
    
    print("❌ Не удалось запустить скрапер ни одним способом")
    return False

def check_notifications():
    """Этап 4: Проверка уведомлений"""
    print_step(4, "ПРОВЕРКА УВЕДОМЛЕНИЙ")
    
    print("📱 Проверяем отправку уведомлений...")
    print("⏰ Ждем 3 минуты для завершения цикла уведомлений...")
    
    # Мониторим логи notification worker
    for i in range(3):
        print(f"⏳ Проверка {i+1}/3 (через {(i+1)*60} секунд)...")
        time.sleep(60)
        
        # Проверяем логи
        print("📋 Проверяем логи notification worker...")
        run_command(
            "railway logs --service telegram-bot-notifications",
            "Получаем последние логи"
        )
    
    print("✅ Проверка завершена. Проверьте Telegram на наличие уведомлений!")
    return True

def restart_services():
    """Этап 0: Перезапуск сервисов"""
    print_step(0, "ПЕРЕЗАПУСК СЕРВИСОВ")
    
    services = [
        "telegram-bot-notifications",
        "SCRAPPER",
        "telegram-bot"
    ]
    
    success = True
    for service in services:
        print(f"\n🔄 Перезапускаем сервис: {service}")
        # Railway restart command
        success &= run_command(
            f"railway service restart --service {service}",
            f"Перезапуск {service}"
        )
    
    if success:
        print("⏰ Ждем 30 секунд для полного запуска сервисов...")
        time.sleep(30)
    
    return success

def main():
    """Главная функция тестирования"""
    print("🚀 ЗАПУСК ПОЛНОГО ТЕСТИРОВАНИЯ ITA_RENT_BOT")
    print(f"🕐 Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Этап 0: Перезапуск сервисов
    if not restart_services():
        print("❌ Не удалось перезапустить сервисы!")
        return False
    
    # Этап 1: Обновление пользователя
    if not update_user_to_premium():
        print("❌ Не удалось обновить пользователя до Premium!")
        return False
    
    # Этап 2: Настройка переменных
    if not update_railway_variables():
        print("❌ Не удалось настроить переменные Railway!")
        return False
    
    # Ждем применения переменных
    print("⏰ Ждем 60 секунд для применения переменных...")
    time.sleep(60)
    
    # Этап 3: Запуск скрапера
    if not trigger_scraper():
        print("❌ Не удалось запустить скрапер!")
        return False
    
    # Этап 4: Проверка уведомлений
    if not check_notifications():
        print("❌ Ошибка при проверке уведомлений!")
        return False
    
    print("\n🎉 ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!")
    print("📱 Проверьте Telegram на наличие уведомлений о новых объявлениях")
    print("📋 При необходимости проверьте логи сервисов в Railway Dashboard")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⏹️ Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        sys.exit(1) 