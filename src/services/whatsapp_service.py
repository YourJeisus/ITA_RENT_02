"""
WhatsApp сервис для ITA_RENT_BOT
Интеграция с WhatsApp Business API для отправки уведомлений
"""
import logging
import aiohttp
import asyncio
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.database import get_db
from src.crud.crud_user import get_user_by_whatsapp_phone, link_whatsapp, get_by_whatsapp_phone

# Добавляем поддержку Twilio SDK
try:
    from twilio.rest import Client as TwilioClient
    TWILIO_SDK_AVAILABLE = True
except ImportError:
    TwilioClient = None
    TWILIO_SDK_AVAILABLE = False

# Настройка логирования
logger = logging.getLogger(__name__)


class WhatsAppService:
    """Основной класс для работы с WhatsApp Business API"""
    
    def __init__(self):
        if not settings.WHATSAPP_ENABLED:
            logger.warning("⚠️ WhatsApp уведомления отключены в конфигурации")
            return
            
        if not all([
            settings.WHATSAPP_API_URL,
            settings.WHATSAPP_API_TOKEN,
            settings.WHATSAPP_PHONE_NUMBER_ID
        ]):
            raise ValueError("❌ Не все обязательные настройки WhatsApp API настроены")
        
        self.api_url = settings.WHATSAPP_API_URL
        self.api_token = settings.WHATSAPP_API_TOKEN
        self.phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
        self.business_account_id = settings.WHATSAPP_BUSINESS_ACCOUNT_ID
        self.db_session = None
        
        # Headers для API запросов
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }
    
    def get_db(self) -> Session:
        """Получение сессии базы данных"""
        if not self.db_session:
            self.db_session = next(get_db())
        return self.db_session
    
    async def send_text_message_sdk(self, phone_number: str, message: str) -> bool:
        """
        Отправка через Twilio Python SDK (предпочтительный метод)
        """
        if not TWILIO_SDK_AVAILABLE:
            logger.warning("Twilio SDK не установлен, используем HTTP API")
            return await self.send_text_message_http(phone_number, message)
        
        if not settings.WHATSAPP_ENABLED:
            logger.warning("WhatsApp уведомления отключены")
            return False
            
        try:
            # Форматируем номер телефона
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if clean_phone.startswith('7'):  # Россия
                clean_phone = '7' + clean_phone[1:]
            elif clean_phone.startswith('39'):  # Италия
                clean_phone = '39' + clean_phone[2:]
            elif not clean_phone.startswith(('7', '39', '1', '44', '49', '33')):
                clean_phone = '39' + clean_phone
            
            logger.info(f"📱 Отправка WhatsApp через Twilio SDK на номер {clean_phone[:3]}***{clean_phone[-3:]}")
            
            # Создаем Twilio клиент
            client = TwilioClient(
                settings.WHATSAPP_BUSINESS_ACCOUNT_ID,
                settings.WHATSAPP_API_TOKEN
            )
            
            # Отправляем сообщение
            twilio_message = client.messages.create(
                from_=settings.WHATSAPP_PHONE_NUMBER_ID,
                to=f"whatsapp:+{clean_phone}",
                body=message
            )
            
            logger.info(f"✅ Twilio SDK: сообщение отправлено успешно (SID: {twilio_message.sid})")
            logger.info(f"📊 Статус: {twilio_message.status}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки через Twilio SDK: {e}")
            # Fallback на HTTP API
            return await self.send_text_message_http(phone_number, message)

    async def send_text_message_http(self, phone_number: str, message: str) -> bool:
        """
        Отправка текстового сообщения через WhatsApp Business API
        Поддерживает Meta Business API и Twilio API
        
        Args:
            phone_number: Номер телефона в международном формате (без +)
            message: Текст сообщения
            
        Returns:
            bool: Успешность отправки
        """
        if not settings.WHATSAPP_ENABLED:
            logger.warning("WhatsApp уведомления отключены")
            return False
            
        try:
            # Форматируем номер телефона (убираем все символы кроме цифр)
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            
            # WhatsApp API требует номер без + и с кодом страны
            if clean_phone.startswith('7'):  # Россия
                clean_phone = '7' + clean_phone[1:]
            elif clean_phone.startswith('39'):  # Италия
                clean_phone = '39' + clean_phone[2:]
            elif not clean_phone.startswith(('7', '39', '1', '44', '49', '33')):
                # Если код страны не распознан, добавляем код Италии
                clean_phone = '39' + clean_phone
            
            # Определяем тип API по URL
            is_twilio = 'twilio.com' in self.api_url.lower()
            
            if is_twilio:
                # Twilio API формат
                payload = {
                    "From": self.phone_number_id,  # whatsapp:+14155238886
                    "To": f"whatsapp:+{clean_phone}",
                    "Body": message
                }
                
                # Twilio использует Basic Auth
                import base64
                auth_string = f"{settings.WHATSAPP_BUSINESS_ACCOUNT_ID}:{self.api_token}"
                auth_bytes = auth_string.encode('ascii')
                auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
                
                headers = {
                    "Authorization": f"Basic {auth_b64}",
                    "Content-Type": "application/x-www-form-urlencoded"
                }
                
                url = self.api_url
                
                logger.info(f"📱 Отправка Twilio WhatsApp сообщения на номер {clean_phone[:3]}***{clean_phone[-3:]}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        data=payload,  # Twilio принимает form data
                        headers=headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        if response.status in [200, 201]:
                            result = await response.json()
                            message_sid = result.get("sid")
                            logger.info(f"✅ Twilio WhatsApp сообщение отправлено успешно (SID: {message_sid})")
                            return True
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ Ошибка отправки Twilio WhatsApp: {response.status} - {error_text}")
                            return False
            else:
                # Meta Business API формат (по умолчанию)
                url = f"{self.api_url}/{self.phone_number_id}/messages"
                
                payload = {
                    "messaging_product": "whatsapp",
                    "to": clean_phone,
                    "type": "text",
                    "text": {
                        "body": message
                    }
                }
                
                logger.info(f"📱 Отправка Meta WhatsApp сообщения на номер {clean_phone[:3]}***{clean_phone[-3:]}")
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        json=payload,
                        headers=self.headers,
                        timeout=aiohttp.ClientTimeout(total=30)
                    ) as response:
                        
                        if response.status == 200:
                            result = await response.json()
                            message_id = result.get("messages", [{}])[0].get("id")
                            logger.info(f"✅ Meta WhatsApp сообщение отправлено успешно (ID: {message_id})")
                            return True
                        else:
                            error_text = await response.text()
                            logger.error(f"❌ Ошибка отправки Meta WhatsApp: {response.status} - {error_text}")
                            return False
                        
        except Exception as e:
            logger.error(f"❌ Исключение при отправке WhatsApp сообщения: {e}")
            return False

    async def send_text_message(self, phone_number: str, message: str) -> bool:
        """
        Основной метод отправки - сначала пробует SDK, потом HTTP
        """
        if TWILIO_SDK_AVAILABLE:
            return await self.send_text_message_sdk(phone_number, message)
        else:
            return await self.send_text_message_http(phone_number, message)

    async def send_media_message(self, phone_number: str, message: str, media_url: str) -> bool:
        """
        Отправка сообщения с изображением через Twilio SDK
        """
        if not TWILIO_SDK_AVAILABLE:
            logger.warning("Twilio SDK не установлен, медиа сообщения недоступны")
            return await self.send_text_message_http(phone_number, message)
        
        if not settings.WHATSAPP_ENABLED:
            logger.warning("WhatsApp уведомления отключены")
            return False
            
        try:
            # Форматируем номер телефона
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            if clean_phone.startswith('7'):  # Россия
                clean_phone = '7' + clean_phone[1:]
            elif clean_phone.startswith('39'):  # Италия
                clean_phone = '39' + clean_phone[2:]
            elif not clean_phone.startswith(('7', '39', '1', '44', '49', '33')):
                clean_phone = '39' + clean_phone
            
            logger.info(f"📱🖼️ Отправка WhatsApp с изображением на номер {clean_phone[:3]}***{clean_phone[-3:]}")
            
            # Создаем Twilio клиент
            client = TwilioClient(
                settings.WHATSAPP_BUSINESS_ACCOUNT_ID,
                settings.WHATSAPP_API_TOKEN
            )
            
            # Отправляем сообщение с медиа
            twilio_message = client.messages.create(
                from_=settings.WHATSAPP_PHONE_NUMBER_ID,
                to=f"whatsapp:+{clean_phone}",
                body=message,
                media_url=[media_url]  # Twilio принимает список URL изображений
            )
            
            logger.info(f"✅ Twilio SDK: медиа сообщение отправлено успешно (SID: {twilio_message.sid})")
            logger.info(f"📊 Статус: {twilio_message.status}")
            logger.info(f"🖼️ Изображение: {media_url}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки медиа через Twilio SDK: {e}")
            # Fallback на текстовое сообщение
            logger.info("🔄 Fallback: отправляем без изображения")
            return await self.send_text_message(phone_number, message)

    def format_single_listing_message(self, listing: Dict, filter_name: str = "Ваш фильтр") -> str:
        """
        Форматирует сообщение для одного объявления (как в Telegram)
        """
        def clean_text(text) -> str:
            return str(text).strip() if text else ""
        
        # Заголовок
        title = clean_text(listing.get('title', 'Без названия'))
        if len(title) > 60:
            title = title[:57] + "..."
        
        message_parts = [
            f"🏠 *{title}*",
            ""
        ]
        
        # Основная информация
        price = listing.get('price')
        if price:
            price_line = f"💰 *{price}€/месяц*"
            
            # Добавляем характеристики
            details = []
            if listing.get('rooms'):
                details.append(f"🚪 {listing['rooms']} комн.")
            if listing.get('area'):
                details.append(f"📐 {listing['area']} м²")
            
            if details:
                price_line += " • " + " • ".join(details)
            
            message_parts.append(price_line)
        
        # Адрес
        address = clean_text(listing.get('address', ''))
        city = clean_text(listing.get('city', ''))
        if address:
            location = f"📍 {address}"
            if city and city not in address:
                location += f", {city}"
            message_parts.append(location)
        
        # Дополнительная информация
        extras = []
        if listing.get('furnished'):
            extras.append("🪑 Меблированная")
        if listing.get('pets_allowed'):
            extras.append("🐕 Питомцы ОК")
        if listing.get('floor') is not None:
            extras.append(f"🏢 {listing['floor']} этаж")
        
        if extras:
            message_parts.append(" • ".join(extras))
        
        # Ссылка
        if listing.get('url'):
            url = clean_text(listing['url'])
            domain = url.split('/')[2] if '/' in url else listing.get('source', 'источник')
            message_parts.append(f"🔗 {domain}")
        
        message_parts.append("")
        message_parts.append(f"📍 _Фильтр: {filter_name}_")
        message_parts.append("📱 *ITA_RENT_BOT*")
        
        return "\n".join(message_parts)

    async def send_individual_listings(self, phone_number: str, listings: List[Dict], filter_name: str) -> int:
        """
        Отправка каждого объявления отдельным сообщением с изображением
        Возвращает количество успешно отправленных сообщений
        """
        successful_count = 0
        
        logger.info(f"📱 Отправка {len(listings)} объявлений по отдельности на номер {phone_number}")
        
        for i, listing in enumerate(listings[:5], 1):  # Максимум 5 объявлений
            try:
                # Форматируем сообщение для одного объявления
                message = self.format_single_listing_message(listing, filter_name)
                
                # Проверяем наличие изображений
                images = listing.get('images', [])
                
                success = False
                if images and len(images) > 0:
                    # Пробуем отправить с первым изображением
                    first_image = images[0]
                    if first_image and (first_image.startswith('http://') or first_image.startswith('https://')):
                        logger.info(f"📸 Объявление {i}: отправляем с изображением")
                        success = await self.send_media_message(phone_number, message, first_image)
                
                # Если не получилось с изображением, отправляем без него
                if not success:
                    logger.info(f"📝 Объявление {i}: отправляем без изображения")
                    success = await self.send_text_message(phone_number, message)
                
                if success:
                    successful_count += 1
                    logger.info(f"✅ Объявление {i}/{len(listings)} отправлено")
                else:
                    logger.error(f"❌ Не удалось отправить объявление {i}")
                
                # Пауза между сообщениями (чтобы не спамить)
                if i < len(listings):
                    await asyncio.sleep(2)
                    
            except Exception as e:
                logger.error(f"❌ Ошибка отправки объявления {i}: {e}")
                continue
        
        logger.info(f"📊 Отправлено {successful_count} из {len(listings)} объявлений")
        return successful_count

    async def send_listing_with_images(self, phone_number: str, listings: List[Dict], filter_name: str) -> bool:
        """
        Отправка объявлений - каждое отдельным сообщением с фото (как в Telegram)
        """
        try:
            if not listings:
                return False
            
            # Отправляем каждое объявление отдельно
            successful_count = await self.send_individual_listings(phone_number, listings, filter_name)
            
            # Считаем успехом если отправлено хотя бы одно объявление
            return successful_count > 0
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки объявлений с изображениями: {e}")
            return False
    
    async def send_template_message(self, phone_number: str, template_name: str, 
                                  language_code: str = "ru", parameters: List[str] = None) -> bool:
        """
        Отправка шаблонного сообщения через WhatsApp Business API
        
        Args:
            phone_number: Номер телефона
            template_name: Название шаблона
            language_code: Код языка (ru, en, it)
            parameters: Параметры для подстановки в шаблон
            
        Returns:
            bool: Успешность отправки
        """
        if not settings.WHATSAPP_ENABLED:
            return False
            
        try:
            clean_phone = ''.join(filter(str.isdigit, phone_number))
            
            url = f"{self.api_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": clean_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {"code": language_code}
                }
            }
            
            # Добавляем параметры если они есть
            if parameters:
                payload["template"]["components"] = [{
                    "type": "body",
                    "parameters": [{"type": "text", "text": param} for param in parameters]
                }]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    url,
                    json=payload,
                    headers=self.headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        message_id = result.get("messages", [{}])[0].get("id")
                        logger.info(f"✅ WhatsApp шаблон отправлен успешно (ID: {message_id})")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Ошибка отправки WhatsApp шаблона: {response.status} - {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"❌ Исключение при отправке WhatsApp шаблона: {e}")
            return False
    
    def format_listing_message(self, listings: List[Dict], filter_name: str = "Ваш фильтр") -> str:
        """
        Форматирование сообщения с объявлениями для WhatsApp
        
        Args:
            listings: Список объявлений
            filter_name: Название фильтра
            
        Returns:
            str: Отформатированное сообщение
        """
        if not listings:
            return "Новых объявлений по вашему фильтру пока нет."
        
        # Ограничиваем до 3 объявлений на сообщение (WhatsApp лимит)
        listings_to_show = listings[:3]
        count = len(listings)
        
        message = f"🏠 *Новые объявления!*\n\n"
        message += f"📍 Фильтр: _{filter_name}_\n"
        message += f"📊 Найдено: {count} объявлений\n\n"
        
        for i, listing in enumerate(listings_to_show, 1):
            price = listing.get('price', 'Цена не указана')
            title = listing.get('title', 'Без названия')[:80]  # Ограничение длины
            address = listing.get('address', listing.get('city', 'Адрес не указан'))[:60]
            source = listing.get('source', '').upper()
            rooms = listing.get('rooms')
            area = listing.get('area')
            
            message += f"*{i}. {title}*\n"
            message += f"💰 {price}€/мес"
            
            if rooms:
                message += f" • 🚪 {rooms} комн."
            if area:
                message += f" • 📐 {area} м²"
            
            message += f"\n📍 {address}\n"
            message += f"🔗 {listing.get('url', 'Ссылка недоступна')}\n"
            message += f"📱 Источник: {source}\n\n"
        
        if count > 3:
            message += f"... и еще {count - 3} объявлений\n\n"
        
        message += "💡 _Уведомления можно настроить в личном кабинете_"
        
        return message
    
    async def verify_phone_number(self, phone_number: str) -> bool:
        """
        Проверка возможности отправки сообщений на номер
        
        Args:
            phone_number: Номер телефона для проверки
            
        Returns:
            bool: Можно ли отправлять сообщения на этот номер
        """
        if not settings.WHATSAPP_ENABLED:
            return False
            
        try:
            # Отправляем тестовое сообщение для проверки
            test_message = "Тест подключения WhatsApp уведомлений ITA_RENT_BOT"
            return await self.send_text_message(phone_number, test_message)
            
        except Exception as e:
            logger.error(f"❌ Ошибка проверки номера WhatsApp {phone_number}: {e}")
            return False


# Глобальный экземпляр сервиса
whatsapp_service = None

def get_whatsapp_service() -> Optional[WhatsAppService]:
    """Получение глобального экземпляра WhatsApp сервиса"""
    global whatsapp_service
    
    if not settings.WHATSAPP_ENABLED:
        return None
        
    if whatsapp_service is None:
        try:
            whatsapp_service = WhatsAppService()
            logger.info("✅ WhatsApp сервис инициализирован")
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации WhatsApp сервиса: {e}")
            return None
    
    return whatsapp_service


# Функции для отправки уведомлений (аналогично telegram_bot.py)
async def send_whatsapp_notification(
    phone_number: str, 
    message: str
) -> bool:
    """
    Отправка WhatsApp уведомления пользователю
    
    Args:
        phone_number: Номер телефона в международном формате
        message: Текст сообщения
        
    Returns:
        bool: Успешность отправки
    """
    service = get_whatsapp_service()
    if not service:
        logger.warning("WhatsApp сервис недоступен")
        return False
    
    return await service.send_text_message(phone_number, message)


async def send_whatsapp_listing_notification(
    phone_number: str,
    listings: List[Dict],
    filter_name: str = "Ваш фильтр"
) -> bool:
    """
    Отправка уведомления с объявлениями через WhatsApp с поддержкой изображений
    
    Args:
        phone_number: Номер телефона
        listings: Список объявлений
        filter_name: Название фильтра
        
    Returns:
        bool: Успешность отправки
    """
    service = get_whatsapp_service()
    if not service:
        return False
    
    # Используем новый метод с поддержкой изображений
    return await service.send_listing_with_images(phone_number, listings, filter_name) 