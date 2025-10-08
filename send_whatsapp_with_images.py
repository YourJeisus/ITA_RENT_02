#!/usr/bin/env python3
"""
Тестирование WhatsApp сообщений с изображениями
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

def create_listings_with_real_images():
    """Создает объявления с реальными изображениями"""
    
    listings = [
        {
            'title': 'Квартира в историческом центре Рима',
            'price': 1800.0,
            'rooms': 3,
            'area': 85.0,
            'address': 'Via del Corso, 123',
            'city': 'Roma',
            'url': 'https://www.idealista.it/immobile/12345678/',
            'source': 'idealista',
            'images': [
                'https://images.unsplash.com/photo-1523217582562-09d0def993a6?w=800',  # Красивая квартира
                'https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=800'   # Интерьер
            ],
            'furnished': True,
            'pets_allowed': False,
            'floor': 2
        },
        {
            'title': 'Студия у моря в Римини',
            'price': 1200.0,
            'rooms': 1,
            'area': 45.0,
            'address': 'Via Marina, 45',
            'city': 'Rimini',
            'url': 'https://www.immobiliare.it/annunci/67890123/',
            'source': 'immobiliare',
            'images': [
                'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800',  # Квартира у моря
                'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800'   # Вид на море
            ],
            'furnished': True,
            'pets_allowed': True,
            'floor': 3
        },
        {
            'title': 'Таунхаус с садом в Тоскане',
            'price': 2500.0,
            'rooms': 4,
            'area': 120.0,
            'address': 'Via Verde, 78',
            'city': 'Siena',
            'url': 'https://www.subito.it/affitto/casa_123456789.htm',
            'source': 'subito',
            'images': [
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800',  # Тосканский дом
                'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=800'   # Сад
            ],
            'furnished': False,
            'pets_allowed': True,
            'floor': 0
        }
    ]
    
    return listings

async def test_whatsapp_with_images():
    """Тестирует отправку WhatsApp с изображениями"""
    
    logger.info("🖼️ ТЕСТИРОВАНИЕ WHATSAPP С ИЗОБРАЖЕНИЯМИ")
    logger.info("=" * 60)
    
    try:
        # Инициализируем сервис
        whatsapp_service = WhatsAppService()
        
        # Создаем объявления с изображениями
        listings = create_listings_with_real_images()
        filter_name = "Тестовый фильтр с изображениями"
        phone_number = "+79992394439"
        
        logger.info(f"📱 Отправка на номер: {phone_number}")
        logger.info(f"🏠 Объявлений: {len(listings)}")
        logger.info(f"🖼️ Изображений в первом объявлении: {len(listings[0]['images'])}")
        
        # Проверяем изображения
        first_listing = listings[0]
        if first_listing['images']:
            logger.info(f"📸 Первое изображение: {first_listing['images'][0]}")
        
        # Отправляем с изображениями
        success = await whatsapp_service.send_listing_with_images(
            phone_number, 
            listings, 
            filter_name
        )
        
        if success:
            logger.info("✅ Сообщение с изображениями отправлено успешно!")
            logger.info("📱 Проверьте WhatsApp - должно прийти:")
            logger.info("   • Текстовое сообщение с деталями объявлений")
            logger.info("   • Изображение первого объявления")
            logger.info("   • Красивое форматирование")
            return True
        else:
            logger.error("❌ Не удалось отправить сообщение")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        return False

async def test_single_image():
    """Тестирует отправку одного изображения"""
    
    logger.info("\n🖼️ ТЕСТ ОТПРАВКИ ОДНОГО ИЗОБРАЖЕНИЯ")
    logger.info("-" * 40)
    
    try:
        whatsapp_service = WhatsAppService()
        
        message = """🏠 Роскошная квартира в Риме!

📍 Via del Corso, 123, Centro Storico
💰 1800€/месяц • 🚪 3 комн. • 📐 85 м²
🪑 Меблированная • 🏢 2 этаж

📱 ITA_RENT_BOT - находим лучшее жилье в Италии!"""

        # Красивое изображение квартиры
        image_url = "https://images.unsplash.com/photo-1523217582562-09d0def993a6?w=800&q=80"
        
        logger.info(f"📸 Отправляем изображение: {image_url}")
        
        success = await whatsapp_service.send_media_message(
            "+79992394439",
            message,
            image_url
        )
        
        if success:
            logger.info("✅ Одиночное изображение отправлено!")
        else:
            logger.error("❌ Не удалось отправить изображение")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Ошибка отправки изображения: {e}")
        return False

async def main():
    """Главная функция"""
    
    # Проверяем настройки
    if not settings.WHATSAPP_ENABLED:
        logger.error("❌ WhatsApp отключен в настройках")
        return
    
    logger.info("✅ WhatsApp включен в настройках")
    logger.info(f"📱 Twilio Account: {settings.WHATSAPP_BUSINESS_ACCOUNT_ID}")
    
    # Тест 1: Объявления с изображениями
    test1_success = await test_whatsapp_with_images()
    
    # Пауза между тестами
    await asyncio.sleep(3)
    
    # Тест 2: Одиночное изображение
    test2_success = await test_single_image()
    
    # Результаты
    logger.info("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    logger.info("=" * 60)
    logger.info(f"   Объявления с изображениями: {'✅' if test1_success else '❌'}")
    logger.info(f"   Одиночное изображение: {'✅' if test2_success else '❌'}")
    
    if test1_success and test2_success:
        logger.info("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        logger.info("   WhatsApp с изображениями работает идеально!")
        logger.info("   Теперь ваши уведомления будут как в Telegram - с фото!")
    else:
        logger.info("\n⚠️ Некоторые тесты не прошли")
        logger.info("   Но система все равно будет работать без изображений")
    
    logger.info("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 