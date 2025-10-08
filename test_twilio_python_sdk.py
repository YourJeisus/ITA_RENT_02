#!/usr/bin/env python3
"""
Тест Twilio WhatsApp через Python SDK
"""
from twilio.rest import Client
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_twilio_sdk():
    """Тест отправки WhatsApp сообщения через Twilio Python SDK"""
    
    # Ваши данные
    account_sid = 'AC92e7c88b81200efad3d3747c98f8f389'
    auth_token = 'c87adc86bb7b1de2157944867628e815'
    
    logger.info("🚀 Тестируем Twilio WhatsApp через Python SDK")
    logger.info(f"Account SID: {account_sid}")
    logger.info(f"Auth Token: {auth_token[:8]}***{auth_token[-8:]}")
    
    try:
        # Создаем клиент Twilio
        client = Client(account_sid, auth_token)
        logger.info("✅ Twilio клиент создан успешно")
        
        # Отправляем сообщение
        logger.info("📤 Отправляем тестовое сообщение...")
        
        message = client.messages.create(
            from_='whatsapp:+14155238886',
            body='🏠 Тест ITA_RENT_BOT через Twilio Python SDK! Если вы получили это сообщение, значит все работает отлично! ✅',
            to='whatsapp:+79992394439'
        )
        
        logger.info(f"✅ Сообщение отправлено успешно!")
        logger.info(f"📝 Message SID: {message.sid}")
        logger.info(f"📊 Статус: {message.status}")
        logger.info(f"🚛 Направление: {message.direction}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки сообщения: {e}")
        logger.error(f"   Тип ошибки: {type(e).__name__}")
        return False

def test_account_info():
    """Проверка информации об аккаунте"""
    
    account_sid = 'AC92e7c88b81200efad3d3747c98f8f389'
    auth_token = 'c87adc86bb7b1de2157944867628e815'
    
    try:
        client = Client(account_sid, auth_token)
        
        # Получаем информацию об аккаунте
        account = client.api.accounts(account_sid).fetch()
        
        logger.info("📊 ИНФОРМАЦИЯ ОБ АККАУНТЕ:")
        logger.info(f"   Friendly Name: {account.friendly_name}")
        logger.info(f"   Status: {account.status}")
        logger.info(f"   Type: {account.type}")
        logger.info(f"   Date Created: {account.date_created}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ошибка получения информации об аккаунте: {e}")
        return False

if __name__ == "__main__":
    logger.info("🧪 ТЕСТИРОВАНИЕ TWILIO PYTHON SDK")
    logger.info("=" * 60)
    
    # Тест 1: Информация об аккаунте
    logger.info("\n🧪 Тест 1: Проверка аккаунта")
    account_ok = test_account_info()
    
    if account_ok:
        # Тест 2: Отправка сообщения
        logger.info("\n🧪 Тест 2: Отправка WhatsApp сообщения")
        message_ok = test_twilio_sdk()
        
        if message_ok:
            logger.info("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
            logger.info("   Twilio Python SDK работает корректно")
            logger.info("   Проверьте WhatsApp на номере +79992394439")
        else:
            logger.info("\n⚠️ Тест отправки сообщения не пройден")
    else:
        logger.info("\n❌ Не удалось подключиться к аккаунту Twilio")
    
    logger.info("\n" + "=" * 60) 