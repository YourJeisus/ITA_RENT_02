#!/usr/bin/env python3
"""
Тест отправки отдельных объявлений в WhatsApp (как в Telegram)
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

def create_sample_listings():
    """Создает образцы объявлений с изображениями"""
    
    listings = [
        {
            'title': 'Роскошная квартира в центре Рима с видом на Колизей',
            'price': 2200.0,
            'rooms': 3,
            'area': 95.0,
            'address': 'Via dei Fori Imperiali, 15',
            'city': 'Roma',
            'url': 'https://www.idealista.it/immobile/98765432/',
            'source': 'idealista',
            'images': [
                'https://images.unsplash.com/photo-1523217582562-09d0def993a6?w=800&q=80',  # Красивая квартира
            ],
            'furnished': True,
            'pets_allowed': False,
            'floor': 3
        },
        {
            'title': 'Уютная студия рядом с пляжем Римини',
            'price': 1400.0,
            'rooms': 1,
            'area': 50.0,
            'address': 'Viale Regina Elena, 28',
            'city': 'Rimini',
            'url': 'https://www.immobiliare.it/annunci/33445566/',
            'source': 'immobiliare',
            'images': [
                'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800&q=80',  # Квартира у моря
            ],
            'furnished': True,
            'pets_allowed': True,
            'floor': 2
        },
        {
            'title': 'Дом в Тоскане с виноградником',
            'price': 3500.0,
            'rooms': 5,
            'area': 180.0,
            'address': 'Strada del Chianti, 42',
            'city': 'Siena',
            'url': 'https://www.subito.it/affitto/villa_987654321.htm',
            'source': 'subito',
            'images': [
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&q=80',  # Тосканский дом
            ],
            'furnished': False,
            'pets_allowed': True,
            'floor': 0
        }
    ]
    
    return listings

async def test_individual_listings():
    """Тестирует отправку отдельных объявлений"""
    
    logger.info("📱 ТЕСТИРОВАНИЕ ОТДЕЛЬНЫХ ОБЪЯВЛЕНИЙ В WHATSAPP")
    logger.info("=" * 60)
    
    try:
        # Инициализируем сервис
        whatsapp_service = WhatsAppService()
        
        # Создаем объявления
        listings = create_sample_listings()
        filter_name = "Элитная недвижимость в Италии"
        phone_number = "+79992394439"
        
        logger.info(f"📱 Отправка на номер: {phone_number}")
        logger.info(f"🏠 Объявлений: {len(listings)}")
        logger.info(f"📸 Каждое объявление будет отправлено:")
        logger.info("   • Отдельным сообщением")
        logger.info("   • С собственным изображением")
        logger.info("   • С полной информацией")
        logger.info("   • С паузой 2 секунды между сообщениями")
        
        # Показываем что будет отправлено
        for i, listing in enumerate(listings, 1):
            logger.info(f"   {i}. {listing['title'][:30]}... - {listing['price']}€")
        
        logger.info("\n🚀 Начинаем отправку...")
        
        # Отправляем объявления
        success = await whatsapp_service.send_listing_with_images(
            phone_number, 
            listings, 
            filter_name
        )
        
        if success:
            logger.info("\n✅ ОТПРАВКА ЗАВЕРШЕНА УСПЕШНО!")
            logger.info("📱 Проверьте WhatsApp - должны прийти:")
            logger.info("   • 3 отдельных сообщения")
            logger.info("   • Каждое с красивым изображением")
            logger.info("   • Полная информация по каждому объявлению")
            logger.info("   • Профессиональное форматирование")
            return True
        else:
            logger.error("\n❌ Не удалось отправить объявления")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка тестирования: {e}")
        return False

async def test_single_listing():
    """Тестирует форматирование одного объявления"""
    
    logger.info("\n📝 ТЕСТ ФОРМАТИРОВАНИЯ ОДНОГО ОБЪЯВЛЕНИЯ")
    logger.info("-" * 50)
    
    try:
        whatsapp_service = WhatsAppService()
        
        # Создаем одно объявление
        listing = {
            'title': 'Пентхаус с террасой в Милане',
            'price': 4500.0,
            'rooms': 4,
            'area': 120.0,
            'address': 'Corso Buenos Aires, 88',
            'city': 'Milano',
            'url': 'https://www.idealista.it/immobile/premium123/',
            'source': 'idealista',
            'images': [
                'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800&q=80',
            ],
            'furnished': True,
            'pets_allowed': False,
            'floor': 12
        }
        
        # Форматируем сообщение
        message = whatsapp_service.format_single_listing_message(listing, "VIP недвижимость")
        
        logger.info("📝 Форматированное сообщение:")
        logger.info("-" * 30)
        logger.info(message)
        logger.info("-" * 30)
        
        # Отправляем это сообщение
        logger.info("📤 Отправляем это сообщение...")
        
        success = await whatsapp_service.send_media_message(
            "+79992394439",
            message,
            listing['images'][0]
        )
        
        if success:
            logger.info("✅ Одиночное объявление отправлено!")
        else:
            logger.error("❌ Не удалось отправить")
            
        return success
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}")
        return False

async def main():
    """Главная функция"""
    
    # Проверяем настройки
    if not settings.WHATSAPP_ENABLED:
        logger.error("❌ WhatsApp отключен в настройках")
        return
    
    logger.info("✅ WhatsApp включен в настройках")
    logger.info(f"📱 Twilio Account: {settings.WHATSAPP_BUSINESS_ACCOUNT_ID}")
    
    # Тест 1: Отдельные объявления
    test1_success = await test_individual_listings()
    
    # Пауза между тестами
    await asyncio.sleep(5)
    
    # Тест 2: Форматирование одного объявления
    test2_success = await test_single_listing()
    
    # Результаты
    logger.info("\n📊 РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
    logger.info("=" * 60)
    logger.info(f"   Отдельные объявления: {'✅' if test1_success else '❌'}")
    logger.info(f"   Одиночное объявление: {'✅' if test2_success else '❌'}")
    
    if test1_success and test2_success:
        logger.info("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        logger.info("   WhatsApp теперь работает КАК В TELEGRAM!")
        logger.info("   • Каждое объявление - отдельным сообщением")
        logger.info("   • С собственным изображением")
        logger.info("   • Красивое форматирование")
        logger.info("   • Профессиональный вид")
    else:
        logger.info("\n⚠️ Некоторые тесты не прошли")
    
    logger.info("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main()) 