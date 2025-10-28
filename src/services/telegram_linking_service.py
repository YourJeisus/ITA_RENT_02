"""
Сервис для управления кодами привязки Telegram
Хранит коды связки в памяти с автоматическим истечением
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class TelegramLinkingService:
    """Управление кодами привязки Telegram аккаунтов"""
    
    def __init__(self):
        self.codes: Dict[str, Dict[str, Any]] = {}
        self.code_ttl_hours = 24  # Коды действительны 24 часа
    
    def store_code(self, code: str, telegram_id: int, telegram_username: Optional[str], chat_id: int) -> None:
        """
        Сохранить код привязки
        
        Args:
            code: Код для привязки
            telegram_id: ID Telegram пользователя
            telegram_username: Username Telegram пользователя
            chat_id: ID чата Telegram
        """
        self.codes[code] = {
            'telegram_id': telegram_id,
            'telegram_username': telegram_username,
            'chat_id': chat_id,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(hours=self.code_ttl_hours)
        }
        logger.info(f"📝 Код привязки создан: {code} для Telegram user {telegram_id}")
    
    def get_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Получить данные по коду с проверкой истечения
        
        Args:
            code: Код для проверки
            
        Returns:
            Данные кода если действителен, иначе None
        """
        if code not in self.codes:
            logger.warning(f"⚠️ Код не найден: {code}")
            return None
        
        code_data = self.codes[code]
        
        # Проверяем истечение
        if datetime.now() > code_data['expires_at']:
            logger.warning(f"⚠️ Код истек: {code}")
            del self.codes[code]
            return None
        
        logger.info(f"✅ Код найден и действителен: {code}")
        return code_data
    
    def remove_code(self, code: str) -> bool:
        """
        Удалить использованный код
        
        Args:
            code: Код для удаления
            
        Returns:
            True если код был удален, False если не найден
        """
        if code in self.codes:
            del self.codes[code]
            logger.info(f"🗑️ Код удален: {code}")
            return True
        
        logger.warning(f"⚠️ Код для удаления не найден: {code}")
        return False
    
    def cleanup_expired(self) -> int:
        """
        Очистить истекшие коды (можно запускать периодически)
        
        Returns:
            Количество удаленных кодов
        """
        expired_codes = [
            code for code, data in self.codes.items()
            if datetime.now() > data['expires_at']
        ]
        
        for code in expired_codes:
            del self.codes[code]
        
        if expired_codes:
            logger.info(f"🧹 Очищено истекших кодов: {len(expired_codes)}")
        
        return len(expired_codes)
    
    def get_stats(self) -> Dict[str, int]:
        """Получить статистику активных кодов"""
        return {
            'total_codes': len(self.codes),
            'valid_codes': len([
                code for code, data in self.codes.items()
                if datetime.now() <= data['expires_at']
            ])
        }


# Глобальный экземпляр сервиса
telegram_linking_service = TelegramLinkingService()
