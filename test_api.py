#!/usr/bin/env python3
"""
Простой скрипт для тестирования API endpoints
"""
import asyncio
import requests
import json
from datetime import datetime

# Конфигурация
API_BASE_URL = "http://localhost:8000/api/v1"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_PASSWORD = "testpassword123"

def print_section(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 30)

def test_health():
    print_section("1. Health Check")
    try:
        response = requests.get(f"{API_BASE_URL}/../health", timeout=10)
        print_response(response)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_auth():
    print_section("2. Authentication")
    
    # Регистрация
    print("Регистрация пользователя:")
    register_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "first_name": "Test",
        "last_name": "User"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json=register_data, timeout=10)
        print_response(response)
        
        if response.status_code == 422:
            print("Пользователь уже существует, пробуем войти...")
        
        # Вход
        print("Вход пользователя:")
        login_data = {
            "username": TEST_USER_EMAIL,  # FastAPI OAuth2 использует username
            "password": TEST_USER_PASSWORD
        }
        
        response = requests.post(f"{API_BASE_URL}/auth/login", data=login_data, timeout=10)
        print_response(response)
        
        if response.status_code == 200:
            token_data = response.json()
            return token_data.get("access_token")
        
    except Exception as e:
        print(f"Error: {e}")
    
    return None

def test_listings(token=None):
    print_section("3. Listings API")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Получение городов
    print("Получение списка городов:")
    try:
        response = requests.get(f"{API_BASE_URL}/listings/suggestions/cities", headers=headers, timeout=10)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}")
    
    # Поиск объявлений
    print("Поиск объявлений:")
    search_params = {
        "city": "Roma",
        "min_price": 500,
        "max_price": 2000,
        "limit": 5
    }
    
    try:
        response = requests.get(f"{API_BASE_URL}/listings/", params=search_params, headers=headers, timeout=30)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}")
    
    # Статистика базы данных
    print("Статистика базы данных:")
    try:
        response = requests.get(f"{API_BASE_URL}/listings/stats/database", headers=headers, timeout=10)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}")

def test_filters(token):
    if not token:
        print("Нет токена для тестирования фильтров")
        return
    
    print_section("4. Filters API")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    # Получение фильтров пользователя
    print("Получение фильтров пользователя:")
    try:
        response = requests.get(f"{API_BASE_URL}/filters/", headers=headers, timeout=10)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}")
    
    # Создание фильтра
    print("Создание нового фильтра:")
    filter_data = {
        "name": "Тестовый фильтр",
        "city": "Roma",
        "min_price": 800,
        "max_price": 1500,
        "min_rooms": 2,
        "property_type": "apartment",
        "notification_enabled": True
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/filters/", json=filter_data, headers=headers, timeout=10)
        print_response(response)
        
        if response.status_code == 200:
            filter_id = response.json().get("id")
            
            # Тестирование фильтра
            if filter_id:
                print(f"Тестирование фильтра {filter_id}:")
                response = requests.post(f"{API_BASE_URL}/filters/{filter_id}/test", headers=headers, timeout=10)
                print_response(response)
        
    except Exception as e:
        print(f"Error: {e}")

def test_scraping():
    print_section("5. Scraping API")
    
    # Запуск парсинга
    print("Запуск парсинга:")
    scraping_data = {
        "sources": ["idealista"],
        "city": "Roma",
        "max_pages": 1
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/scraping/run", json=scraping_data, timeout=60)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}")
    
    # Статус парсинга
    print("Статус парсинга:")
    try:
        response = requests.get(f"{API_BASE_URL}/scraping/status", timeout=10)
        print_response(response)
    except Exception as e:
        print(f"Error: {e}")

def main():
    print(f"🚀 Тестирование API: {API_BASE_URL}")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. Health check
    if not test_health():
        print("❌ API недоступен!")
        return
    
    print("✅ API доступен!")
    
    # 2. Аутентификация
    token = test_auth()
    if token:
        print("✅ Аутентификация прошла успешно!")
    else:
        print("❌ Ошибка аутентификации!")
    
    # 3. Тестирование listings
    test_listings(token)
    
    # 4. Тестирование фильтров (требует аутентификации)
    if token:
        test_filters(token)
    
    # 5. Тестирование парсинга
    test_scraping()
    
    print_section("Тестирование завершено")
    print("🎉 Все тесты выполнены!")

if __name__ == "__main__":
    main() 