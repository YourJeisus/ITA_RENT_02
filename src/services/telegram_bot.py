"""
Telegram бот для ITA_RENT_BOT
MVP версия с базовыми командами для связывания аккаунтов и уведомлений
"""
import logging
import asyncio
from typing import Optional, Dict, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, 
    CallbackQueryHandler, ContextTypes, filters
)
from sqlalchemy.orm import Session

from src.core.config import settings
from src.db.database import get_db
from src.crud.crud_user import get_user_by_email, link_telegram, get_by_telegram_chat_id
from src.crud.crud_filter import filter as crud_filter
from src.schemas.user import UserTelegramLink

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBotService:
    """Основной класс Telegram бота для MVP"""
    
    def __init__(self):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN не настроен в конфигурации")
        
        self.token = settings.TELEGRAM_BOT_TOKEN
        self.application = None
        self.db_session = None
    
    def get_db(self) -> Session:
        """Получение сессии базы данных"""
        if not self.db_session:
            self.db_session = next(get_db())
        return self.db_session
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Команда /start - приветствие и инструкция по регистрации"""
        chat_id = str(update.effective_chat.id)
        
        try:
            user = get_by_telegram_chat_id(self.get_db(), telegram_chat_id=chat_id)
        except Exception as e:
            logger.error(f"Ошибка при поиске пользователя по chat_id {chat_id}: {e}")
            user = None
        
        if user:
            # Пользователь уже привязан
            await update.message.reply_text(
                f"👋 Привет, {user.first_name or 'друг'}!\n\n"
                f"Ваш аккаунт уже привязан к email: {user.email}\n"
                f"📱 Используйте /help для просмотра доступных команд."
            )
        else:
            # Новый пользователь
            welcome_text = (
                "🏠 *Добро пожаловать в ITA RENT BOT!*\n\n"
                "Я помогу вам найти идеальную недвижимость в Италии и буду "
                "присылать уведомления о новых предложениях.\n\n"
                "*Как начать:*\n"
                "1️⃣ Зарегистрируйтесь на нашем сайте\n"
                "2️⃣ Используйте команду `/register email@example.com` для связывания аккаунта\n"
                "3️⃣ Настройте фильтры поиска и получайте уведомления!\n\n"
                "📌 *Команды:*\n"
                "/register - связать аккаунт\n"
                "/help - справка\n"
                "/status - информация об аккаунте"
            )
            
            await update.message.reply_text(
                welcome_text,
                parse_mode='Markdown'
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Команда /help - справка по командам"""
        help_text = (
            "🤖 *Справка по командам ITA RENT BOT*\n\n"
            "*Основные команды:*\n"
            "/start - начало работы\n"
            "/register email - связать аккаунт с вашим email\n"
            "/status - информация о подписке и фильтрах\n"
            "/filters - список ваших фильтров\n"
            "/pause - приостановить уведомления\n"
            "/resume - возобновить уведомления\n\n"
            "*Полезная информация:*\n"
            "• Уведомления приходят автоматически при появлении новых объявлений\n"
            "• В бесплатной версии: 1 фильтр, уведомления раз в день\n"
            "• В Premium: 5 фильтров, уведомления каждые 30 минут\n\n"
            "💬 Если у вас есть вопросы, напишите нам!"
        )
        
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def register_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Команда /register - связывание с аккаунтом по email"""
        chat_id = str(update.effective_chat.id)
        
        # Проверяем, не привязан ли уже аккаунт
        existing_user = get_by_telegram_chat_id(self.get_db(), telegram_chat_id=chat_id)
        if existing_user:
            await update.message.reply_text(
                f"✅ Ваш аккаунт уже привязан к email: {existing_user.email}\n"
                f"Используйте /status для просмотра информации."
            )
            return
        
        # Проверяем аргументы команды
        if not context.args:
            await update.message.reply_text(
                "❌ Укажите ваш email для связывания аккаунта.\n\n"
                "*Пример:* `/register your@email.com`\n\n"
                "📝 Email должен совпадать с тем, который вы использовали "
                "при регистрации на сайте.",
                parse_mode='Markdown'
            )
            return
        
        email = context.args[0].lower().strip()
        
        # Проверяем формат email (базовая проверка)
        if '@' not in email or '.' not in email:
            await update.message.reply_text(
                "❌ Неверный формат email. Попробуйте еще раз.\n"
                "*Пример:* `/register your@email.com`",
                parse_mode='Markdown'
            )
            return
        
        # Ищем пользователя в базе данных
        user = get_user_by_email(self.get_db(), email=email)
        if not user:
            await update.message.reply_text(
                f"❌ Пользователь с email `{email}` не найден.\n\n"
                f"🔗 Сначала зарегистрируйтесь на нашем сайте, "
                f"а затем привяжите аккаунт здесь.",
                parse_mode='Markdown'
            )
            return
        
        # Проверяем, не привязан ли аккаунт к другому Telegram
        if user.telegram_chat_id and user.telegram_chat_id != chat_id:
            await update.message.reply_text(
                "❌ Этот аккаунт уже привязан к другому Telegram.\n"
                "Если это ваш аккаунт, обратитесь в поддержку."
            )
            return
        
        # Привязываем аккаунт
        try:
            telegram_username = update.effective_user.username
            link_telegram(
                self.get_db(),
                user_id=user.id,
                telegram_chat_id=chat_id,
                telegram_username=telegram_username
            )
            
            await update.message.reply_text(
                f"✅ *Аккаунт успешно привязан!*\n\n"
                f"📧 Email: {user.email}\n"
                f"👤 Имя: {user.first_name or 'Не указано'}\n"
                f"💎 Подписка: {user.subscription_type.title()}\n\n"
                f"🔔 Теперь вы будете получать уведомления о новых объявлениях.\n"
                f"Используйте /filters для просмотра фильтров поиска.",
                parse_mode='Markdown'
            )
            
        except Exception as e:
            logger.error(f"Ошибка при привязке аккаунта: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при привязке аккаунта. "
                "Попробуйте позже или обратитесь в поддержку."
            )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Команда /status - информация о подписках"""
        chat_id = str(update.effective_chat.id)
        user = get_by_telegram_chat_id(self.get_db(), telegram_chat_id=chat_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Аккаунт не привязан.\n"
                "Используйте `/register your@email.com` для связывания.",
                parse_mode='Markdown'
            )
            return
        
        # Получаем информацию о фильтрах
        filters = crud_filter.get_by_user(self.get_db(), user_id=user.id)
        active_filters = [f for f in filters if f.is_active]
        
        # Определяем лимиты подписки
        if user.subscription_type == "premium":
            max_filters = 5
            notification_frequency = "каждые 30 минут"
        else:
            max_filters = 1
            notification_frequency = "раз в день"
        
        status_text = (
            f"📊 *Статус аккаунта*\n\n"
            f"👤 *Профиль:*\n"
            f"📧 Email: {user.email}\n"
            f"👤 Имя: {user.first_name or 'Не указано'}\n"
            f"📅 Регистрация: {user.created_at.strftime('%d.%m.%Y')}\n\n"
            f"💎 *Подписка:* {user.subscription_type.title()}\n"
            f"🔔 *Уведомления:* {notification_frequency}\n\n"
            f"🔍 *Фильтры поиска:*\n"
            f"📋 Активных: {len(active_filters)}/{max_filters}\n"
            f"💤 Неактивных: {len(filters) - len(active_filters)}\n\n"
        )
        
        if active_filters:
            status_text += "📝 *Активные фильтры:*\n"
            for f in active_filters[:3]:  # Показываем первые 3
                status_text += f"• {f.name} ({f.city or 'Любой город'})\n"
            
            if len(active_filters) > 3:
                status_text += f"• ...и еще {len(active_filters) - 3}\n"
        
        status_text += f"\n📱 Используйте /filters для управления фильтрами"
        
        await update.message.reply_text(status_text, parse_mode='Markdown')
    
    async def filters_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Команда /filters - список активных фильтров"""
        chat_id = str(update.effective_chat.id)
        user = get_by_telegram_chat_id(self.get_db(), telegram_chat_id=chat_id)
        
        if not user:
            await update.message.reply_text(
                "❌ Аккаунт не привязан.\n"
                "Используйте `/register your@email.com` для связывания.",
                parse_mode='Markdown'
            )
            return
        
        filters = crud_filter.get_by_user(self.get_db(), user_id=user.id)
        
        if not filters:
            await update.message.reply_text(
                "📋 У вас пока нет фильтров поиска.\n\n"
                "🌐 Создайте фильтры на нашем сайте и получайте "
                "уведомления о новых объявлениях!"
            )
            return
        
        filters_text = "🔍 *Ваши фильтры поиска:*\n\n"
        
        for f in filters:
            status_emoji = "🟢" if f.is_active else "🔴"
            filters_text += f"{status_emoji} *{f.name}*\n"
            
            if f.city:
                filters_text += f"📍 {f.city}\n"
            
            price_range = ""
            if f.min_price and f.max_price:
                price_range = f"{f.min_price}-{f.max_price}€"
            elif f.min_price:
                price_range = f"от {f.min_price}€"
            elif f.max_price:
                price_range = f"до {f.max_price}€"
            
            if price_range:
                filters_text += f"💰 {price_range}\n"
            
            if f.property_type:
                filters_text += f"🏠 {f.property_type}\n"
            
            filters_text += f"⏰ Создан: {f.created_at.strftime('%d.%m.%Y')}\n"
            filters_text += f"/pause_{f.id} - {'включить' if not f.is_active else 'отключить'}\n\n"
        
        filters_text += "🌐 Управляйте фильтрами на нашем сайте"
        
        await update.message.reply_text(filters_text, parse_mode='Markdown')
    
    async def pause_filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Команда для приостановки/возобновления фильтра"""
        # Эта функция будет обрабатывать команды вида /pause_123
        command_text = update.message.text
        if '_' in command_text:
            try:
                filter_id = int(command_text.split('_')[1])
                chat_id = str(update.effective_chat.id)
                user = get_by_telegram_chat_id(self.get_db(), telegram_chat_id=chat_id)
                
                if not user:
                    await update.message.reply_text("❌ Аккаунт не привязан.")
                    return
                
                filter_obj = crud_filter.get(self.get_db(), id=filter_id)
                
                if not filter_obj or filter_obj.user_id != user.id:
                    await update.message.reply_text("❌ Фильтр не найден.")
                    return
                
                # Переключаем статус фильтра
                new_status = not filter_obj.is_active
                filter_obj.is_active = new_status
                self.get_db().commit()
                
                status_text = "включен" if new_status else "отключен"
                await update.message.reply_text(
                    f"✅ Фильтр *{filter_obj.name}* {status_text}.",
                    parse_mode='Markdown'
                )
                
            except (ValueError, IndexError):
                await update.message.reply_text("❌ Неверный формат команды.")
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка неизвестных команд"""
        await update.message.reply_text(
            "❓ Неизвестная команда.\n"
            "Используйте /help для просмотра доступных команд."
        )
    
    def setup_handlers(self):
        """Настройка обработчиков команд"""
        if not self.application:
            raise ValueError("Application не инициализирован")
        
        # Основные команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("register", self.register_command))
        self.application.add_handler(CommandHandler("status", self.status_command))
        self.application.add_handler(CommandHandler("filters", self.filters_command))
        self.application.add_handler(CommandHandler("dbtest", self.dbtest_command))
        
        # Обработчик команд приостановки фильтров
        self.application.add_handler(MessageHandler(
            filters.Regex(r'^/pause_\d+$'), 
            self.pause_filter_command
        ))
        
        # Обработчик неизвестных команд
        self.application.add_handler(MessageHandler(
            filters.COMMAND, 
            self.unknown_command
        ))
    
    async def initialize(self):
        """Инициализация бота"""
        self.application = Application.builder().token(self.token).build()
        self.setup_handlers()
        
        # Инициализируем приложение
        await self.application.initialize()
        logger.info("Telegram бот инициализирован")
    
    async def start_polling(self):
        """Запуск бота в режиме polling"""
        if not self.application:
            await self.initialize()
        
        logger.info("Запуск Telegram бота в режиме polling...")
        await self.application.start()
        await self.application.updater.start_polling()
        
        try:
            # Блокируем выполнение
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Остановка бота...")
        finally:
            await self.application.updater.stop()
            await self.application.stop()
    
    async def dbtest_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Команда /dbtest - тест подключения к базе данных"""
        chat_id = str(update.effective_chat.id)
        
        try:
            # Проверяем подключение к базе данных
            db = self.get_db()
            
            # Считаем количество пользователей
            from src.db.models import User, Listing
            users_count = db.query(User).count()
            listings_count = db.query(Listing).count()
            
            # Проверяем текущего пользователя по chat_id
            current_user = get_by_telegram_chat_id(db, telegram_chat_id=chat_id)
            
            response = f"🔍 **Тест базы данных:**\n\n"
            response += f"✅ Подключение к БД: Успешно\n"
            response += f"👥 Всего пользователей: {users_count}\n"
            response += f"🏠 Всего объявлений: {listings_count}\n"
            response += f"🤖 Ваш chat_id: `{chat_id}`\n"
            
            if current_user:
                response += f"✅ Ваш аккаунт найден: {current_user.email}\n"
                response += f"🆔 Ваш ID: {current_user.id}\n"
            else:
                response += f"❌ Ваш аккаунт не привязан к Telegram\n"
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Ошибка в команде /dbtest для chat_id {chat_id}: {e}")
            await update.message.reply_text(
                f"❌ **Ошибка теста БД:**\n\n"
                f"```\n{str(e)}\n```\n\n"
                f"Chat ID: `{chat_id}`", 
                parse_mode='Markdown'
            )

    async def stop(self):
        """Остановка бота"""
        if self.application:
            await self.application.stop()
            logger.info("Telegram бот остановлен")


# Глобальный экземпляр бота
telegram_bot = TelegramBotService()


async def send_notification_to_user(
    telegram_chat_id: str, 
    message: str, 
    parse_mode: str = 'Markdown'
) -> bool:
    """
    Отправка уведомления пользователю
    Используется системой уведомлений
    """
    try:
        if not telegram_bot.application:
            await telegram_bot.initialize()
        
        await telegram_bot.application.bot.send_message(
            chat_id=telegram_chat_id,
            text=message,
            parse_mode=parse_mode
        )
        
        logger.info(f"Уведомление отправлено пользователю {telegram_chat_id}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка отправки уведомления: {e}")
        return False


if __name__ == "__main__":
    """Запуск бота для тестирования"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    async def main():
        bot = TelegramBotService()
        await bot.start_polling()
    
    asyncio.run(main()) 