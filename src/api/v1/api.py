"""
Главный роутер для API v1
"""
from fastapi import APIRouter

from src.api.v1 import auth, users

api_router = APIRouter()

# Подключаем роутеры
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])

# В будущем добавим другие роутеры:
# api_router.include_router(listings.router, prefix="/listings", tags=["listings"])
# api_router.include_router(filters.router, prefix="/filters", tags=["filters"]) 