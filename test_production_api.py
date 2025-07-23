#!/usr/bin/env python3
"""
Скрипт для тестирования production API в Railway
"""
import requests
import json
import sys
from datetime import datetime

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def print_response(response):
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text[:500]}...")
    print("-" * 40)

def test_backend_health(backend_url):
    """Тестирование health check backend"""
    print_section("Backend Health Check")
    
    try:
        response = requests.get(f"{backend_url}/health", timeout=10)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                print("✅ Backend работает корректно")
                return True
            else:
                print("❌ Backend возвращает неверный статус")
                return False
        else:
            print("❌ Backend недоступен")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к backend: {e}")
        return False

def test_frontend(frontend_url):
    """Тестирование frontend"""
    print_section("Frontend Check")
    
    try:
        response = requests.get(frontend_url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            if "<title>" in content and "ITA Rent" in content:
                print("✅ Frontend загружается корректно")
                return True
            else:
                print("⚠️  Frontend загружается, но контент может быть неверным")
                print(f"Title найден: {'<title>' in content}")
                return True
        else:
            print("❌ Frontend недоступен")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка подключения к frontend: {e}")
        return False

def test_api_endpoints(backend_url):
    """Тестирование основных API endpoints"""
    print_section("API Endpoints Test")
    
    endpoints = [
        ("/", "Root endpoint"),
        ("/docs", "API Documentation"),
        ("/api/v1/listings/suggestions/cities", "Cities list"),
        ("/api/v1/listings/stats/database", "Database stats"),
    ]
    
    results = []
    
    for endpoint, description in endpoints:
        try:
            print(f"\nТестирование: {description}")
            response = requests.get(f"{backend_url}{endpoint}", timeout=15)
            print(f"  Status: {response.status_code}")
            
            if response.status_code in [200, 307]:  # 307 для редиректов docs
                print(f"  ✅ {description} работает")
                results.append(True)
            else:
                print(f"  ❌ {description} недоступен")
                results.append(False)
                
        except Exception as e:
            print(f"  ❌ Ошибка при тестировании {description}: {e}")
            results.append(False)
    
    return all(results)

def test_cors(backend_url, frontend_url):
    """Тестирование CORS настроек"""
    print_section("CORS Configuration Test")
    
    try:
        # Проверяем CORS headers
        response = requests.options(f"{backend_url}/api/v1/listings/", 
                                  headers={
                                      "Origin": frontend_url,
                                      "Access-Control-Request-Method": "GET"
                                  }, timeout=10)
        
        print(f"CORS preflight status: {response.status_code}")
        
        cors_headers = {
            "Access-Control-Allow-Origin": response.headers.get("Access-Control-Allow-Origin"),
            "Access-Control-Allow-Methods": response.headers.get("Access-Control-Allow-Methods"),
            "Access-Control-Allow-Headers": response.headers.get("Access-Control-Allow-Headers"),
        }
        
        print("CORS Headers:")
        for header, value in cors_headers.items():
            if value:
                print(f"  ✅ {header}: {value}")
            else:
                print(f"  ❌ {header}: Not set")
        
        # Проверяем что frontend URL разрешен
        allowed_origin = cors_headers["Access-Control-Allow-Origin"]
        if allowed_origin == "*" or frontend_url in str(allowed_origin):
            print("✅ CORS настроен корректно для frontend")
            return True
        else:
            print("❌ CORS может блокировать запросы с frontend")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке CORS: {e}")
        return False

def test_database_connection(backend_url):
    """Тестирование подключения к базе данных"""
    print_section("Database Connection Test")
    
    try:
        response = requests.get(f"{backend_url}/api/v1/listings/stats/database", timeout=15)
        print_response(response)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and "stats" in data:
                stats = data["stats"]
                print("✅ База данных подключена")
                print(f"  Всего объявлений: {stats.get('total_listings', 'N/A')}")
                print(f"  Активных объявлений: {stats.get('active_listings', 'N/A')}")
                return True
            else:
                print("❌ База данных недоступна или пуста")
                return False
        else:
            print("❌ Не удается получить статистику базы данных")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка при проверке базы данных: {e}")
        return False

def main():
    if len(sys.argv) != 3:
        print("Использование: python test_production_api.py <backend_url> <frontend_url>")
        print("Пример: python test_production_api.py https://backend.railway.app https://frontend.railway.app")
        return 1
    
    backend_url = sys.argv[1].rstrip('/')
    frontend_url = sys.argv[2].rstrip('/')
    
    print("🚀 Тестирование Production API в Railway")
    print("=" * 60)
    print(f"Backend URL: {backend_url}")
    print(f"Frontend URL: {frontend_url}")
    print(f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Backend Health Check", lambda: test_backend_health(backend_url)),
        ("Frontend Check", lambda: test_frontend(frontend_url)),
        ("API Endpoints", lambda: test_api_endpoints(backend_url)),
        ("CORS Configuration", lambda: test_cors(backend_url, frontend_url)),
        ("Database Connection", lambda: test_database_connection(backend_url)),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Критическая ошибка в тесте {test_name}: {e}")
            results.append((test_name, False))
    
    print_section("Результаты тестирования")
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nИтого: {passed}/{total} тестов пройдено")
    
    if passed == total:
        print("\n🎉 Все тесты пройдены! Production API работает корректно")
        print("\n📋 Следующие шаги:")
        print("1. Проверьте фронтенд в браузере")
        print("2. Протестируйте основные пользовательские сценарии")
        print("3. Настройте мониторинг и алерты")
        return 0
    else:
        print(f"\n❌ {total - passed} тестов провалено. Требуется исправление")
        print("\n🔧 Рекомендации:")
        print("1. Проверьте логи деплоя в Railway Dashboard")
        print("2. Убедитесь что все переменные окружения настроены")
        print("3. Проверьте статус всех сервисов")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 