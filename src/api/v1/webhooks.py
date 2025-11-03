"""
Webhook endpoints для приема результатов от внешних сервисов
"""
from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import logging

from src.parsers.idealista_crawler import IdealistaCrawler
from src.crud.crud_listing import create_listing
from src.db.database import get_db
from src.db.models import Listing

logger = logging.getLogger(__name__)

router = APIRouter()


class ScraperWebhookPayload(BaseModel):
    """Payload от ScraperAPI Crawler webhook"""
    job_id: str
    status: str
    url: str
    html: Optional[str] = None
    status_code: Optional[int] = None
    error: Optional[str] = None


@router.post("/scraper")
async def scraper_webhook(
    payload: ScraperWebhookPayload,
    background_tasks: BackgroundTasks,
    request: Request
):
    """
    Webhook для получения результатов от ScraperAPI Crawler
    
    Вызывается автоматически когда Crawler обрабатывает страницу
    """
    try:
        logger.info(f"📬 Получен webhook от Crawler")
        logger.info(f"   Job ID: {payload.job_id}")
        logger.info(f"   Status: {payload.status}")
        logger.info(f"   URL: {payload.url}")
        logger.info(f"   Status Code: {payload.status_code}")
        
        # Проверяем успешность
        if payload.status != "finished" or not payload.html:
            logger.warning(f"⚠️ Неуспешный результат: {payload.error or 'No HTML'}")
            return {"status": "received", "processed": False}
        
        # Обрабатываем HTML в фоне
        background_tasks.add_task(
            process_crawler_result,
            payload.job_id,
            payload.url,
            payload.html
        )
        
        return {
            "status": "received",
            "processed": True,
            "job_id": payload.job_id
        }
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def process_crawler_result(job_id: str, page_url: str, html_content: str):
    """
    Обрабатывает результат от crawler в фоне
    
    Args:
        job_id: ID задачи crawler
        page_url: URL обработанной страницы
        html_content: HTML контент
    """
    try:
        logger.info(f"🔄 Обрабатываем результат crawler")
        logger.info(f"   Job ID: {job_id}")
        logger.info(f"   URL: {page_url}")
        
        # Создаем парсер
        crawler = IdealistaCrawler()
        
        # Парсим объявления
        listings = crawler.parse_listing_from_html(html_content, page_url)
        
        if not listings:
            logger.info(f"📄 Объявлений не найдено на странице {page_url}")
            return
        
        logger.info(f"📋 Найдено {len(listings)} объявлений")
        
        # Сохраняем в БД
        saved_count = 0
        for db in get_db():
            for listing_data in listings:
                try:
                    # Проверяем существует ли уже
                    existing = db.query(Listing).filter(
                        Listing.external_id == listing_data.get('external_id')
                    ).first()
                    
                    if not existing:
                        create_listing(db, listing_data)
                        saved_count += 1
                        logger.debug(f"✅ Создано новое объявление: {listing_data.get('external_id')}")
                    else:
                        logger.debug(f"⏭️  Объявление уже существует: {listing_data.get('external_id')}")
                        
                except Exception as e:
                    logger.error(f"❌ Ошибка сохранения объявления: {e}")
            
            break  # Используем только первую сессию
        
        logger.info(f"💾 Сохранено {saved_count}/{len(listings)} новых объявлений")
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки результата crawler: {e}")


@router.get("/scraper/test")
async def test_scraper_webhook():
    """Тестовый endpoint для проверки работы webhook"""
    return {
        "status": "ok",
        "message": "Scraper webhook is working",
        "endpoint": "/api/v1/webhooks/scraper"
    }

