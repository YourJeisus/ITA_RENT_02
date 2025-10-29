"""
Сервис для управления кодами привязки Telegram
Хранит коды связки в памяти с автоматическим истечением
"""
import logging
import time
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class TelegramLinkingService:
    """
    Сервис для управления временными кодами связки Telegram аккаунтов.
    Использует файловую систему для хранения кодов (работает между процессами).
    """
    def __init__(self, expiry_seconds: int = 86400, storage_dir: str = "/tmp"):  # 24 часа
        self.expiry_seconds = expiry_seconds
        self.storage_dir = Path(storage_dir)
        self.codes_file = self.storage_dir / "telegram_linking_codes.json"
        
        # Создаём директорию если её нет
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"✅ TelegramLinkingService инициализирован. Хранилище: {self.codes_file}")
        logger.info(f"   Коды истекают через {expiry_seconds} секунд.")
    
    def _load_codes(self) -> Dict[str, Dict[str, Any]]:
        """Загружает коды из файла"""
        if self.codes_file.exists():
            try:
                with open(self.codes_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Ошибка чтения файла кодов: {e}")
                return {}
        return {}
    
    def _save_codes(self, codes: Dict[str, Dict[str, Any]]):
        """Сохраняет коды в файл"""
        try:
            with open(self.codes_file, 'w', encoding='utf-8') as f:
                json.dump(codes, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Ошибка сохранения файла кодов: {e}")
    
    def _cleanup_expired(self, codes: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Удаляет истёкшие коды"""
        current_time = time.time()
        valid_codes = {}
        
        for code, data in codes.items():
            if (current_time - data['created_at']) < self.expiry_seconds:
                valid_codes[code] = data
            else:
                logger.debug(f"🗑️ Код '{code}' истек и удален.")
        
        return valid_codes

    def store_code(self, code: str, telegram_id: int, telegram_username: Optional[str], chat_id: int):
        """Сохраняет код связки с данными пользователя Telegram"""
        codes = self._load_codes()
        
        # Очищаем старые коды
        codes = self._cleanup_expired(codes)
        
        # Добавляем новый код
        codes[code] = {
            'telegram_id': telegram_id,
            'telegram_username': telegram_username,
            'chat_id': chat_id,
            'created_at': time.time()
        }
        
        self._save_codes(codes)
        logger.info(f"🔗 Код связки '{code}' сохранен для Telegram ID: {telegram_id}")

    def get_code(self, code: str) -> Optional[Dict[str, Any]]:
        """Возвращает данные по коду, если он действителен"""
        codes = self._load_codes()
        
        # Очищаем старые коды
        codes = self._cleanup_expired(codes)
        self._save_codes(codes)
        
        if code in codes:
            data = codes[code]
            return data
        
        logger.warning(f"❌ Код '{code}' не найден или истек")
        return None

    def remove_code(self, code: str):
        """Удаляет код связки"""
        codes = self._load_codes()
        
        if code in codes:
            del codes[code]
            self._save_codes(codes)
            logger.info(f"🗑️ Код связки '{code}' удален.")

    def find_code_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Находит код связки по Telegram ID пользователя"""
        codes = self._load_codes()
        
        # Очищаем старые коды
        codes = self._cleanup_expired(codes)
        
        for code, data in codes.items():
            if data['telegram_id'] == telegram_id:
                return data
        
        logger.warning(f"❌ Код связки для Telegram ID {telegram_id} не найден или истек")
        return None

telegram_linking_service = TelegramLinkingService()
