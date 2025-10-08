"""
Главный роутер для API v1
"""
from fastapi import APIRouter

from src.api.v1 import auth, users, scraping, listings, filters, telegram, whatsapp

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(scraping.router, prefix="/scraping", tags=["scraping"])
api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
api_router.include_router(filters.router, prefix="/filters", tags=["filters"])
api_router.include_router(telegram.router, prefix="/telegram", tags=["telegram"])
api_router.include_router(whatsapp.router, prefix="/whatsapp", tags=["whatsapp"]) 