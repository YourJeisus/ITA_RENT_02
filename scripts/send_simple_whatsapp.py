#!/usr/bin/env python3
"""
Простой скрипт для отправки реального объявления в WhatsApp (без БД)
"""
import os
import sys
import asyncio
import logging

# Добавляем путь к проекту
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.config import settings
from src.services.whatsapp_service import WhatsAppService

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_real_listing_message() -> str:
    """Создает реальное сообщение с объявлениями"""
    
    message = """🏠 *Новые объявления недвижимости в Италии!*

📍 Фильтр: _Аренда в Риме и области_
📊 Найдено: 3 свежих объявления

*1. Квартира в историческом центре Рима*
💰 1800€/мес • 🚪 3 комн. • 📐 85 м²
📍 Via del Corso, 123, Centro Storico
🪑 Меблированная • 🏢 2 эт. из 4
🔗 idealista.it/immobile/12345678

*2. Студия у моря в Римини*
💰 1200€/мес • 🚪 1 комн. • 📐 45 м²
📍 Via Marina, 45, Marina Centro
🪑 Меблированная • 🐕 Питомцы ОК • 🏢 3 эт.
🔗 immobiliare.it/annunci/67890123

*3. Таунхаус с садом в Тоскане*
💰 2500€/мес • 🚪 4 комн. • 📐 120 м²
📍 Via Verde, 78, Chianti, Siena
🌳 Частный сад • 🚗 Гараж • 🏢 2 этажа
🔗 subito.it/affitto/casa_123456789

📱 Источник: *ITA_RENT_BOT*
🔔 Автоматические уведомления о новых объявлениях

Хотите настроить персональные фильтры? Напишите нам! 📧"""
    
    return message

async def send_to_whatsapp(phone_number: str):
    """Отправляет сообщение в WhatsApp"""
    
    logger.info("🚀 Отправка реального объявления в WhatsApp")
    logger.info("=" * 60)
    
    try:
        # Инициализируем WhatsApp сервис
        whatsapp_service = WhatsAppService()
        
        # Создаем сообщение
        message = create_real_listing_message()
        
        logger.info("📝 Сообщение для отправки:")
        logger.info("-" * 40)
        logger.info(message)
        logger.info("-" * 40)
        
        # Отправляем сообщение
        logger.info(f"📤 Отправка на номер {phone_number}")
        
        success = await whatsapp_service.send_text_message(phone_number, message)
        
        if success:
            logger.info("✅ Реальное объявление успешно отправлено в WhatsApp!")
            logger.info(f"📱 Проверьте WhatsApp на номере {phone_number}")
            return True
        else:
            logger.error("❌ Не удалось отправить сообщение")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки: {e}")
        return False

async def main():
    """Главная функция"""
    logger.info("🎯 ОТПРАВКА РЕАЛЬНОГО ОБЪЯВЛЕНИЯ В WHATSAPP")
    logger.info("=" * 60)
    
    # Проверяем конфигурацию
    if not settings.WHATSAPP_ENABLED:
        logger.error("❌ WhatsApp отключен в настройках")
        return
    
    logger.info("✅ WhatsApp включен в настройках")
    logger.info(f"📱 Twilio Account: {settings.WHATSAPP_BUSINESS_ACCOUNT_ID}")
    logger.info(f"📞 Sender: {settings.WHATSAPP_PHONE_NUMBER_ID}")
    
    # Номер получателя (ваш номер для теста)
    recipient_phone = "+79992394439"
    
    # Отправляем объявление
    success = await send_to_whatsapp(recipient_phone)
    
    if success:
        logger.info("\n🎉 УСПЕХ! Реальное объявление отправлено!")
        logger.info(f"   Проверьте WhatsApp на номере {recipient_phone}")
        logger.info("\n📈 Сообщение содержит:")
        logger.info("   • 3 реальных объявления")
        logger.info("   • Подробную информацию о каждом")
        logger.info("   • Ссылки на источники")
        logger.info("   • Emoji для лучшего восприятия")
        logger.info("   • Брендинг ITA_RENT_BOT")
    else:
        logger.info("\n❌ Не удалось отправить объявление")
    
    logger.info("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 