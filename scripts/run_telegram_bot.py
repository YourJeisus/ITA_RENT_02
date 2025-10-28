#!/usr/bin/env python3
"""
Скрипт запуска Telegram бота для ITA_RENT_BOT
"""
import os
import sys
import asyncio
import logging
from pathlib import Path

# Добавляем корневую папку в путь
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def load_environment():
    """Загрузка переменных окружения"""
    try:
        from dotenv import load_dotenv
        load_dotenv(dotenv_path=ROOT_DIR / '.env')
        logger.info("✅ Переменные окружения загружены")
    except ImportError:
        logger.info("📝 python-dotenv не установлен, используем системные переменные")

def check_required_env_vars():
    """Проверка обязательных переменных окружения"""
    required_vars = {
        "TELEGRAM_BOT_TOKEN": "Токен Telegram бота",
        "DATABASE_URL": "URL базы данных",
        "SECRET_KEY": "Секретный ключ"
    }
    
    missing_vars = []
    for var, description in required_vars.items():
        if not os.getenv(var):
            missing_vars.append(f"{var} ({description})")
    
    if missing_vars:
        logger.error("❌ Отсутствуют обязательные переменные окружения:")
        for var in missing_vars:
            logger.error(f"   - {var}")
        return False
    
    logger.info("✅ Все обязательные переменные окружения установлены")
    return True

async def check_database_connection():
    """Проверка подключения к базе данных с ретраями"""
    max_retries = 10
    retry_delay = 5
    
    for attempt in range(max_retries):
        try:
            from src.db.database import get_db
            from src.db.models import User
            
            # Получаем сессию БД
            db = next(get_db())
            
            # Пробуем выполнить простой запрос
            count = db.query(User).count()
            logger.info(f"✅ База данных доступна. Пользователей: {count}")
            db.close()
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Попытка {attempt + 1}/{max_retries} подключения к БД неуспешна: {e}")
            
            if attempt < max_retries - 1:
                logger.info(f"⏳ Ожидание {retry_delay} секунд перед повторной попыткой...")
                await asyncio.sleep(retry_delay)
            else:
                logger.error("❌ Не удалось подключиться к базе данных")
                return False
    
    return False

async def main():
    """Главная функция"""
    logger.info("🤖 Запуск ITA_RENT_BOT Telegram Bot...")
    
    # Загружаем переменные окружения
    load_environment()
    
    # Проверяем переменные окружения
    if not check_required_env_vars():
        sys.exit(1)
    
    # Проверяем подключение к базе данных
    logger.info("🔍 Проверка подключения к базе данных...")
    if not await check_database_connection():
        logger.error("❌ Критическая ошибка: Нет подключения к базе данных")
        sys.exit(1)
    
    # Запускаем бота
    try:
        from telegram import Update
        from telegram.ext import Application, CommandHandler, ContextTypes
        from src.db.models import User
        from src.db.database import get_db
        import secrets
        import string
        
        # Инициализируем приложение
        application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()
        
        # ========== ОБРАБОТЧИКИ КОМАНД ==========
        
        async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """
            Команда /start - приветствие и предложение связать аккаунт
            """
            user = update.effective_user
            chat_id = update.effective_chat.id
            
            logger.info(f"👤 Новый пользователь Telegram: {user.username} (ID: {user.id})")
            
            # Генерируем код для связки
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            
            # Сохраняем код используя сервис
            from src.services.telegram_linking_service import telegram_linking_service
            telegram_linking_service.store_code(code, user.id, user.username, chat_id)
            
            message = f"""
🏠 Добро пожаловать в ITA Rent Bot!

Я помогу вам получать уведомления о новых объявлениях прямо в Telegram.

**Для связки аккаунта:**
1. Откройте приложение ITA Rent на сайте
2. Перейдите в настройки профиля
3. Нажмите кнопку "Link Telegram"
4. Введите этот код: `{code}`

Код действителен 24 часа.

**Мои команды:**
/help - справка по командам
/status - статус привязки
/settings - настройки уведомлений
            """
            
            await update.message.reply_text(message, parse_mode='Markdown')
            logger.info(f"✅ Код связки отправлен пользователю {user.username}: {code}")
        
        async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """Справка по командам"""
            help_text = """
🤖 **Команды ITA Rent Bot:**

/start - Начало работы и код связки
/help - Эта справка
/status - Проверить статус привязки аккаунта
/settings - Управление настройками уведомлений
/unlink - Отвязать аккаунт от Telegram

**Как начать:**
1. Используйте /start для получения кода
2. Введите код в приложении на сайте
3. Готово! Начните получать уведомления
            """
            await update.message.reply_text(help_text, parse_mode='Markdown')
        
        async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """Проверка статуса привязки"""
            try:
                user_id = update.effective_user.id
                db = next(get_db())
                
                user = db.query(User).filter(User.telegram_chat_id == str(user_id)).first()
                
                if user:
                    status_text = f"""
✅ **Аккаунт привязан!**

Email: `{user.email}`
Имя: {user.first_name} {user.last_name or ''}
Telegram: @{user.telegram_username or 'unknown'}

Уведомления:
• Telegram: {'✅ Включены' if user.telegram_notifications_enabled else '❌ Выключены'}
• Email: {'✅ Включены' if user.email_notifications_enabled else '❌ Выключены'}

Используйте /settings для изменения
                    """
                else:
                    status_text = """
❌ **Аккаунт не привязан**

Используйте /start для получения кода связки
                    """
                
                db.close()
                await update.message.reply_text(status_text, parse_mode='Markdown')
                
            except Exception as e:
                logger.error(f"Ошибка при проверке статуса: {e}")
                await update.message.reply_text("❌ Ошибка при проверке статуса")
        
        async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """Управление настройками"""
            try:
                user_id = update.effective_user.id
                db = next(get_db())
                
                user = db.query(User).filter(User.telegram_chat_id == str(user_id)).first()
                
                if not user:
                    await update.message.reply_text("❌ Аккаунт не привязан. Используйте /start")
                    db.close()
                    return
                
                settings_text = f"""
⚙️ **Ваши настройки уведомлений:**

*Каналы уведомлений:*
• Telegram: {'✅ ON' if user.telegram_notifications_enabled else '❌ OFF'}
• Email: {'✅ ON' if user.email_notifications_enabled else '❌ OFF'}

*Для изменения настроек используйте веб-интерфейс:*
https://ita-rent-02.vercel.app/settings

Там же вы можете:
- Добавлять и удалять фильтры поиска
- Выбирать предпочтительные каналы для каждого фильтра
- Управлять адресом email
                """
                
                db.close()
                await update.message.reply_text(settings_text, parse_mode='Markdown')
                
            except Exception as e:
                logger.error(f"Ошибка при получении настроек: {e}")
                await update.message.reply_text("❌ Ошибка при получении настроек")
        
        async def unlink_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
            """Отвязка аккаунта"""
            try:
                user_id = update.effective_user.id
                db = next(get_db())
                
                user = db.query(User).filter(User.telegram_chat_id == str(user_id)).first()
                
                if not user:
                    await update.message.reply_text("❌ Аккаунт не привязан")
                    db.close()
                    return
                
                user.telegram_chat_id = None
                user.telegram_username = None
                db.commit()
                
                db.close()
                await update.message.reply_text("✅ Аккаунт успешно отвязан от Telegram")
                logger.info(f"✅ Аккаунт отвязан: {user.email}")
                
            except Exception as e:
                logger.error(f"Ошибка при отвязке: {e}")
                await update.message.reply_text("❌ Ошибка при отвязке аккаунта")
        
        # Регистрируем обработчики
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("status", status_command))
        application.add_handler(CommandHandler("settings", settings_command))
        application.add_handler(CommandHandler("unlink", unlink_command))
        
        # Запускаем бота
        logger.info("🚀 Telegram бот запущен и слушает обновления...")
        await application.run_polling()
        
    except ImportError:
        logger.error("❌ Telegram библиотека не установлена")
        logger.info("   Установите: pip install python-telegram-bot")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 