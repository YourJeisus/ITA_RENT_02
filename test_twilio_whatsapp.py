#!/usr/bin/env python3
"""
Тестовый скрипт для проверки Twilio WhatsApp интеграции
Быстрая проверка настроек и отправка тестового сообщения
"""
import os
import sys
import asyncio
import logging
import aiohttp
import base64
from pathlib import Path

# Добавляем корневую папку в путь
sys.path.append(str(Path(__file__).parent))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_environment():
    """Загрузка переменных окружения"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("✅ Переменные окружения загружены")
    except ImportError:
        logger.info("📝 python-dotenv не установлен, используем системные переменные")

def check_twilio_config():
    """Проверка конфигурации Twilio"""
    logger.info("🧪 Проверка конфигурации Twilio...")
    
    # Получаем переменные окружения
    enabled = os.getenv("WHATSAPP_ENABLED", "false").lower() == "true"
    api_url = os.getenv("WHATSAPP_API_URL", "")
    api_token = os.getenv("WHATSAPP_API_TOKEN", "")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")
    account_sid = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    
    logger.info(f"   WHATSAPP_ENABLED: {enabled}")
    logger.info(f"   WHATSAPP_API_URL: {'✅ Настроен' if api_url else '❌ Не настроен'}")
    logger.info(f"   WHATSAPP_API_TOKEN: {'✅ Настроен' if api_token else '❌ Не настроен'}")
    logger.info(f"   WHATSAPP_PHONE_NUMBER_ID: {'✅ Настроен' if phone_id else '❌ Не настроен'}")
    logger.info(f"   WHATSAPP_BUSINESS_ACCOUNT_ID: {'✅ Настроен' if account_sid else '❌ Не настроен'}")
    
    # Проверяем что это Twilio
    is_twilio = 'twilio.com' in api_url.lower() if api_url else False
    logger.info(f"   Провайдер: {'✅ Twilio' if is_twilio else '❌ Не Twilio'}")
    
    if not enabled:
        logger.error("   ❌ WhatsApp отключен! Установите WHATSAPP_ENABLED=true")
        return False
    
    if not all([api_url, api_token, phone_id, account_sid]):
        logger.error("   ❌ Не все обязательные настройки заполнены!")
        return False
    
    if not is_twilio:
        logger.error("   ❌ URL не содержит 'twilio.com'!")
        return False
    
    logger.info("   ✅ Конфигурация Twilio корректна")
    return True

async def test_twilio_api_direct(test_phone: str = None):
    """Прямой тест Twilio API"""
    logger.info("🧪 Прямой тест Twilio API...")
    
    # Получаем настройки
    api_url = os.getenv("WHATSAPP_API_URL")
    api_token = os.getenv("WHATSAPP_API_TOKEN")
    phone_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    account_sid = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
    
    # Номер телефона для тестирования
    if not test_phone:
        test_phone = input("📱 Введите ваш номер телефона для тестирования (например, +393401234567): ").strip()
    
    # Очищаем номер
    clean_phone = ''.join(filter(str.isdigit, test_phone))
    if not clean_phone.startswith(('7', '39', '1', '44', '49', '33')):
        clean_phone = '39' + clean_phone  # Италия по умолчанию
    
    logger.info(f"   Отправка на номер: +{clean_phone}")
    
    try:
        # Подготавливаем данные для Twilio
        payload = {
            "From": phone_id,  # whatsapp:+14155238886
            "To": f"whatsapp:+{clean_phone}",
            "Body": "🏠 Тест WhatsApp уведомлений ITA_RENT_BOT через Twilio!\n\nЕсли вы получили это сообщение, значит все настроено правильно! ✅"
        }
        
        # Twilio Basic Auth
        auth_string = f"{account_sid}:{api_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        headers = {
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        logger.info("   📤 Отправка запроса к Twilio...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                api_url,
                data=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                
                response_text = await response.text()
                
                if response.status in [200, 201]:
                    try:
                        result = await response.json()
                        message_sid = result.get("sid")
                        status = result.get("status")
                        logger.info(f"   ✅ Сообщение отправлено успешно!")
                        logger.info(f"   📝 SID: {message_sid}")
                        logger.info(f"   📊 Статус: {status}")
                        return True
                    except:
                        logger.info(f"   ✅ Сообщение отправлено (статус {response.status})")
                        logger.info(f"   📝 Ответ: {response_text[:200]}")
                        return True
                else:
                    logger.error(f"   ❌ Ошибка отправки: {response.status}")
                    logger.error(f"   📝 Ответ: {response_text}")
                    return False
                    
    except Exception as e:
        logger.error(f"   ❌ Исключение при отправке: {e}")
        return False

async def test_whatsapp_service():
    """Тест через наш WhatsApp сервис"""
    logger.info("🧪 Тест через WhatsApp сервис...")
    
    try:
        from src.services.whatsapp_service import get_whatsapp_service
        
        service = get_whatsapp_service()
        if not service:
            logger.error("   ❌ WhatsApp сервис не инициализирован")
            return False
        
        # Номер телефона для тестирования
        test_phone = input("📱 Введите ваш номер телефона (например, +393401234567): ").strip()
        
        # Тестовое сообщение
        test_message = (
            "🏠 *Тест WhatsApp уведомлений ITA_RENT_BOT*\n\n"
            "Это тестовое сообщение через наш сервис.\n"
            "Если вы получили это сообщение, значит интеграция работает! ✅\n\n"
            "💡 _Теперь вы можете получать уведомления о новых объявлениях._"
        )
        
        logger.info("   📤 Отправка через WhatsApp сервис...")
        success = await service.send_text_message(test_phone, test_message)
        
        if success:
            logger.info("   ✅ Сообщение отправлено через сервис!")
            return True
        else:
            logger.error("   ❌ Ошибка отправки через сервис")
            return False
            
    except Exception as e:
        logger.error(f"   ❌ Ошибка тестирования сервиса: {e}")
        return False

def show_twilio_setup_instructions():
    """Показать инструкции по настройке Twilio"""
    logger.info("📋 ИНСТРУКЦИИ ПО НАСТРОЙКЕ TWILIO:")
    logger.info("")
    logger.info("1. 🌐 Зарегистрируйтесь на https://www.twilio.com/")
    logger.info("2. 📱 Перейдите в Messaging → Try it out → Send a WhatsApp message")
    logger.info("3. 🔧 Активируйте WhatsApp Sandbox:")
    logger.info("   - Отправьте сообщение на указанный номер")
    logger.info("   - Текст: 'join <ваш-код>' (код показан в консоли)")
    logger.info("4. 🔑 Получите API ключи в Account → API keys & tokens:")
    logger.info("   - Account SID (например: AC1234...)")
    logger.info("   - Auth Token (нажмите 'reveal')")
    logger.info("5. ⚙️ Настройте .env файл:")
    logger.info("   WHATSAPP_ENABLED=true")
    logger.info("   WHATSAPP_API_URL=https://api.twilio.com/2010-04-01/Accounts/YOUR_ACCOUNT_SID/Messages.json")
    logger.info("   WHATSAPP_API_TOKEN=ваш_auth_token")
    logger.info("   WHATSAPP_PHONE_NUMBER_ID=whatsapp:+14155238886")
    logger.info("   WHATSAPP_BUSINESS_ACCOUNT_ID=ваш_account_sid")
    logger.info("")

async def main():
    """Главная функция тестирования"""
    logger.info("🚀 Тестирование Twilio WhatsApp интеграции")
    logger.info("=" * 50)
    
    # Загружаем переменные окружения
    load_environment()
    
    # Проверяем конфигурацию
    config_ok = check_twilio_config()
    
    if not config_ok:
        logger.info("")
        show_twilio_setup_instructions()
        return False
    
    logger.info("")
    logger.info("🎯 Выберите тест:")
    logger.info("1. Прямой тест Twilio API")
    logger.info("2. Тест через наш WhatsApp сервис")
    logger.info("3. Оба теста")
    
    choice = input("Введите номер (1-3): ").strip()
    
    results = []
    
    if choice in ['1', '3']:
        logger.info("")
        logger.info("🧪 ПРЯМОЙ ТЕСТ TWILIO API")
        logger.info("-" * 30)
        result1 = await test_twilio_api_direct()
        results.append(("Прямой тест Twilio API", result1))
    
    if choice in ['2', '3']:
        logger.info("")
        logger.info("🧪 ТЕСТ ЧЕРЕЗ WHATSAPP СЕРВИС")
        logger.info("-" * 30)
        result2 = await test_whatsapp_service()
        results.append(("Тест WhatsApp сервиса", result2))
    
    # Итоги
    logger.info("")
    logger.info("📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    logger.info("=" * 50)
    
    all_passed = True
    for test_name, result in results:
        status = "✅ УСПЕХ" if result else "❌ ОШИБКА"
        logger.info(f"   {test_name}: {status}")
        if not result:
            all_passed = False
    
    logger.info("")
    if all_passed:
        logger.info("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        logger.info("   Twilio WhatsApp интеграция работает корректно!")
        logger.info("")
        logger.info("📋 СЛЕДУЮЩИЕ ШАГИ:")
        logger.info("1. 🚀 Запустите WhatsApp worker: python run_whatsapp_worker.py")
        logger.info("2. 🌐 Запустите API сервер: uvicorn src.main:app --reload")
        logger.info("3. 📱 Настройте пользователей через API")
    else:
        logger.info("⚠️ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        logger.info("   Проверьте настройки и повторите тест.")
    
    return all_passed

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("🛑 Тестирование прервано пользователем")
        sys.exit(1)
    except Exception as e:
        logger.error(f"💥 Критическая ошибка: {e}")
        sys.exit(1) 