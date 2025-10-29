"""
Email сервис для ITA_RENT_BOT
Отправка уведомлений по электронной почте через Mailtrap Email API или SMTP
"""
import logging
import asyncio
import requests
from typing import Optional
from datetime import datetime

from src.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email уведомлений через Mailtrap API"""
    
    def __init__(self):
        self.provider = settings.EMAIL_API_PROVIDER
        self.mailtrap_token = settings.MAILTRAP_API_TOKEN
        self.mailtrap_account_id = settings.MAILTRAP_ACCOUNT_ID
        self.sender_email = settings.MAILTRAP_SENDER_EMAIL
        
        # Проверка наличия необходимых настроек
        if self.provider == "mailtrap":
            if not all([self.mailtrap_token, self.mailtrap_account_id]):
                logger.warning("⚠️ Mailtrap Email API настройки не полностью сконфигурированы.")
                self.enabled = False
            else:
                self.enabled = True
                logger.info(f"✅ Email сервис инициализирован: Mailtrap Email API")
        else:
            logger.warning(f"⚠️ Неизвестный email provider: {self.provider}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Проверка доступности email сервиса"""
        return self.enabled
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Отправка email сообщения через Mailtrap API
        
        Args:
            to_email: Email получателя
            subject: Тема письма
            body: Текстовое содержимое письма
            html_body: HTML версия письма (опционально)
            
        Returns:
            bool: Успешность отправки
        """
        if not self.enabled:
            logger.warning("Email сервис отключен, пропускаем отправку")
            return False
        
        try:
            # Используем asyncio.to_thread для асинхронного выполнения синхронного кода
            result = await asyncio.to_thread(
                self._send_via_mailtrap_api,
                to_email,
                subject,
                body,
                html_body
            )
            return result
            
        except Exception as e:
            logger.error(f"❌ Ошибка отправки email на {to_email}: {e}")
            return False
    
    def _send_via_mailtrap_api(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> bool:
        """
        Отправка через Mailtrap API (синхронный метод)
        """
        try:
            url = f"https://send.api.mailtrap.io/api/send"
            
            # Подготавливаем payload
            payload = {
                "from": {
                    "email": self.sender_email,
                    "name": "ITA Rent Bot"
                },
                "to": [
                    {
                        "email": to_email
                    }
                ],
                "subject": subject,
                "text": body,
                "category": "notification"
            }
            
            # Добавляем HTML если есть
            if html_body:
                payload["html"] = html_body
            
            # Отправляем запрос
            headers = {
                "Authorization": f"Bearer {self.mailtrap_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            
            if response.status_code in [200, 201]:
                logger.info(f"✅ Email успешно отправлен на {to_email}")
                return True
            else:
                logger.error(f"❌ Mailtrap API ошибка: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Ошибка Mailtrap API для {to_email}: {e}")
            return False
    
    async def send_listing_notification_email(
        self,
        to_email: str,
        listings: List[dict],
        filter_name: str
    ) -> bool:
        """
        Отправка уведомления о новых объявлениях
        
        Args:
            to_email: Email получателя
            listings: Список объявлений
            filter_name: Название фильтра
            
        Returns:
            bool: Успешность отправки
        """
        if not listings:
            return False
        
        subject = f"🏠 ITA Rent: {len(listings)} новых объявлений по фильтру '{filter_name}'"
        
        # Формируем текстовое сообщение
        body = self._format_listings_text(listings, filter_name)
        
        # Формируем HTML версию (опционально)
        html_body = self._format_listings_html(listings, filter_name)
        
        return await self.send_email(to_email, subject, body, html_body)
    
    def _format_listings_text(self, listings: List[dict], filter_name: str) -> str:
        """Форматирование объявлений в текстовый формат"""
        lines = [
            f"Новые объявления по фильтру: {filter_name}",
            f"Найдено объявлений: {len(listings)}",
            "",
            "=" * 50,
            ""
        ]
        
        for i, listing in enumerate(listings[:10], 1):  # Максимум 10 объявлений
            lines.append(f"{i}. {listing.get('title', 'Без названия')}")
            lines.append(f"   Цена: €{listing.get('price', 'N/A')}")
            
            if listing.get('rooms'):
                lines.append(f"   Комнат: {listing.get('rooms')}")
            
            if listing.get('area'):
                lines.append(f"   Площадь: {listing.get('area')} м²")
            
            if listing.get('address'):
                lines.append(f"   Адрес: {listing.get('address')}")
            
            if listing.get('city'):
                lines.append(f"   Город: {listing.get('city')}")
            
            if listing.get('url'):
                lines.append(f"   Ссылка: {listing.get('url')}")
            
            lines.append("")
        
        if len(listings) > 10:
            lines.append(f"... и еще {len(listings) - 10} объявлений")
            lines.append("")
        
        lines.extend([
            "",
            "=" * 50,
            "",
            "С уважением,",
            "Команда ITA Rent",
            "",
            "Чтобы отписаться от уведомлений, зайдите в настройки вашего профиля."
        ])
        
        return "\n".join(lines)
    
    def _format_listings_html(self, listings: List[dict], filter_name: str) -> str:
        """Форматирование объявлений в HTML формат"""
        listings_html = []
        
        for listing in listings[:10]:  # Максимум 10 объявлений
            listing_html = f"""
            <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 16px; margin-bottom: 16px; background-color: #ffffff;">
                <h3 style="margin: 0 0 8px 0; color: #2563eb;">{listing.get('title', 'Без названия')}</h3>
                <p style="margin: 4px 0; font-size: 18px; font-weight: bold; color: #1f2937;">€{listing.get('price', 'N/A')}</p>
            """
            
            details = []
            if listing.get('rooms'):
                details.append(f"🚪 {listing.get('rooms')} комн.")
            if listing.get('area'):
                details.append(f"📐 {listing.get('area')} м²")
            
            if details:
                listing_html += f'<p style="margin: 4px 0; color: #6b7280;">{" • ".join(details)}</p>'
            
            if listing.get('address'):
                listing_html += f'<p style="margin: 4px 0; color: #6b7280;">📍 {listing.get("address")}</p>'
            
            if listing.get('url'):
                listing_html += f'<p style="margin: 8px 0 0 0;"><a href="{listing.get("url")}" style="color: #2563eb; text-decoration: none;">👀 Посмотреть объявление →</a></p>'
            
            listing_html += "</div>"
            listings_html.append(listing_html)
        
        if len(listings) > 10:
            listings_html.append(f"<p style='text-align: center; color: #6b7280;'>... и еще {len(listings) - 10} объявлений</p>")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; background-color: #f9fafb; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                <div style="background: linear-gradient(135deg, #2563eb 0%, #1e40af 100%); color: white; padding: 24px; text-align: center;">
                    <h1 style="margin: 0; font-size: 24px;">🏠 ITA Rent</h1>
                    <p style="margin: 8px 0 0 0; opacity: 0.9;">Новые объявления для вас</p>
                </div>
                
                <div style="padding: 24px;">
                    <p style="margin: 0 0 16px 0; font-size: 16px; color: #374151;">
                        По вашему фильтру <strong>"{filter_name}"</strong> найдено <strong>{len(listings)} новых объявлений</strong>:
                    </p>
                    
                    {"".join(listings_html)}
                    
                    <div style="border-top: 1px solid #e5e7eb; margin-top: 24px; padding-top: 24px; text-align: center; color: #6b7280; font-size: 14px;">
                        <p>С уважением,<br><strong>Команда ITA Rent</strong></p>
                        <p style="margin-top: 16px;">
                            <a href="https://ita-rent-02.vercel.app/settings" style="color: #2563eb; text-decoration: none;">Управление уведомлениями</a>
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    async def send_test_email(self, to_email: str) -> bool:
        """
        Отправка тестового email
        
        Args:
            to_email: Email получателя
            
        Returns:
            bool: Успешность отправки
        """
        subject = "🧪 ITA Rent: Тестовое уведомление"
        body = """
Привет!

Это тестовое email уведомление из ITA Rent.

Если вы получили это письмо, значит email уведомления настроены правильно! ✅

Теперь вы будете получать уведомления о новых объявлениях согласно вашим фильтрам поиска.

С уважением,
Команда ITA Rent

Чтобы отписаться от уведомлений, зайдите в настройки вашего профиля.
        """
        
        html_body = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; background-color: #f9fafb; margin: 0; padding: 20px;">
            <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); overflow: hidden;">
                <div style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 24px; text-align: center;">
                    <h1 style="margin: 0; font-size: 28px;">🧪 Тестовое уведомление</h1>
                </div>
                
                <div style="padding: 24px;">
                    <p style="font-size: 18px; color: #374151;">Привет!</p>
                    
                    <p style="color: #6b7280;">Это тестовое email уведомление из <strong>ITA Rent</strong>.</p>
                    
                    <div style="background-color: #d1fae5; border-left: 4px solid #10b981; padding: 16px; margin: 16px 0; border-radius: 4px;">
                        <p style="margin: 0; color: #065f46;">✅ Если вы получили это письмо, значит email уведомления настроены правильно!</p>
                    </div>
                    
                    <p style="color: #6b7280;">Теперь вы будете получать уведомления о новых объявлениях согласно вашим фильтрам поиска.</p>
                    
                    <div style="border-top: 1px solid #e5e7eb; margin-top: 24px; padding-top: 24px; text-align: center; color: #6b7280; font-size: 14px;">
                        <p>С уважением,<br><strong>Команда ITA Rent</strong></p>
                        <p style="margin-top: 16px;">
                            <a href="https://ita-rent-02.vercel.app/settings" style="color: #2563eb; text-decoration: none;">Управление уведомлениями</a>
                        </p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        return await self.send_email(to_email, subject, body, html_body)


# Глобальный экземпляр сервиса
email_service = EmailService()

