#!/usr/bin/env python3
"""
Скрипт запуска Telegram бота для ITA_RENT_BOT
"""
import os
import sys
import asyncio
import logging
import warnings
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
            
            logger.info(f"👤 Пользователь Telegram: {user.username} (ID: {user.id})")
            
            # Проверяем есть ли уже привязка
            try:
                db = next(get_db())
                existing_user = db.query(User).filter(User.telegram_chat_id == str(user.id)).first()
                db.close()
                
                if existing_user:
                    # Уже привязан
                    message = f"""
✅ **Ваш аккаунт уже привязан!**

Email: `{existing_user.email}`
Telegram: @{existing_user.telegram_username or user.username}

Используйте:
/status - проверить статус
/settings - управлять уведомлениями
/unlink - отвязать аккаунт
                    """
                    await update.message.reply_text(message, parse_mode='Markdown')
                    logger.info(f"ℹ️ Пользователь {user.username} уже привязан")
                    return
            except Exception as e:
                logger.error(f"Ошибка проверки существующей привязки: {e}")
            
            # Проверяем если уже есть активный код для этого пользователя
            from src.services.telegram_linking_service import telegram_linking_service
            existing_code_data = telegram_linking_service.find_code_by_telegram_id(user.id)
            
            if existing_code_data:
                # Код уже существует и ещё активен
                logger.info(f"ℹ️ Повторный /start - используем существующий код для {user.username}")
                code = None
                # Ищем сам код по данным
                codes_dict = telegram_linking_service._load_codes()
                codes_dict = telegram_linking_service._cleanup_expired(codes_dict)
                for stored_code, data in codes_dict.items():
                    if data['telegram_id'] == user.id:
                        code = stored_code
                        break
                
                if not code:
                    # Если вдруг не нашли, генерируем новый
                    code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
                    telegram_linking_service.store_code(code, user.id, user.username, chat_id)
            else:
                # Генерируем новый код для связки
                code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
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
                telegram_user_id = update.effective_user.id
                telegram_username = update.effective_user.username
                
                logger.info(f"📊 Проверка статуса для {telegram_username} (ID: {telegram_user_id})")
                
                db = next(get_db())
                
                # Ищем пользователя по telegram_chat_id
                # telegram_chat_id хранится как string, поэтому сравниваем со str(telegram_user_id)
                user = db.query(User).filter(User.telegram_chat_id == str(telegram_user_id)).first()
                
                if user:
                    status_text = f"""✅ *Аккаунт привязан!*

📧 Email: {user.email}
📨 Рассылка на: {user.notification_email or user.email}
👤 Имя: {user.first_name} {user.last_name or ''}
💬 Telegram: @{user.telegram_username or 'unknown'}

*Уведомления:*
• Telegram: {'✅ Включены' if user.telegram_notifications_enabled else '❌ Выключены'}
• Email: {'✅ Включены' if user.email_notifications_enabled else '❌ Выключены'}

Используйте /settings для изменения"""
                    logger.info(f"✅ Статус найден: {user.email}")
                else:
                    status_text = """❌ *Аккаунт не привязан*

Используйте /start для получения кода связки и привязки аккаунта."""
                    logger.info(f"ℹ️ Аккаунт {telegram_username} не привязан")
                
                db.close()
                # Отправляем текст без parse_mode чтобы избежать конфликтов с символами типа @
                await update.message.reply_text(status_text)
                
            except Exception as e:
                logger.error(f"❌ Ошибка при проверке статуса: {e}", exc_info=True)
                await update.message.reply_text("❌ Ошибка при проверке статуса. Пожалуйста, попробуйте позже.")
        
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
        
        # Запускаем бота используя lifecycle methods
        logger.info("🚀 Telegram бот запущен и слушает обновления...")
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)
        
        # Будем слушать до завершения
        try:
            # Этот блок будет блокировать до Ctrl+C или ошибки
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("⏹️ Получен сигнал прерывания")
        finally:
            await application.updater.stop()
            await application.stop()
            await application.shutdown()
        
    except ImportError:
        logger.error("❌ Telegram библиотека не установлена")
        logger.info("   Установите: pip install python-telegram-bot")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Подавляем предупреждения о event loop от python-telegram-bot
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        
        # Используем event loop напрямую чтобы не закрывать его после завершения
        loop = asyncio.get_event_loop()
        if loop.is_closed():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Запускаем главную корутину но НЕ закрываем loop
        loop.run_until_complete(main())
            
    except KeyboardInterrupt:
        logger.info("⏹️ Бот остановлен пользователем")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Критическая ошибка в главной функции: {e}")
        sys.exit(1) 