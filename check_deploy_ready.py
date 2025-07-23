#!/usr/bin/env python3
"""
Скрипт проверки готовности к деплою в Railway
"""
import os
import sys
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_files():
    """Проверяем наличие необходимых файлов"""
    print_section("Проверка файлов")
    
    required_files = [
        "Dockerfile.prod",
        "railway.toml",
        "requirements.txt",
        "src/main.py",
        "frontend/Dockerfile.railway",
        "frontend/package.json",
        "alembic.ini",
        "alembic/env.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Отсутствует: {file_path}")
        else:
            print(f"✅ Найден: {file_path}")
    
    return len(missing_files) == 0

def check_railway_config():
    """Проверяем конфигурацию Railway"""
    print_section("Проверка конфигурации Railway")
    
    try:
        with open("railway.toml", "r") as f:
            content = f.read()
            
        if "backend" in content:
            print("✅ Сервис backend настроен")
        else:
            print("❌ Сервис backend не найден в railway.toml")
            return False
            
        if "frontend" in content:
            print("✅ Сервис frontend настроен")
        else:
            print("❌ Сервис frontend не найден в railway.toml")
            return False
            
        if "Dockerfile.prod" in content:
            print("✅ Dockerfile.prod указан для backend")
        else:
            print("❌ Dockerfile.prod не указан для backend")
            
        if "Dockerfile.railway" in content:
            print("✅ Dockerfile.railway указан для frontend")
        else:
            print("❌ Dockerfile.railway не указан для frontend")
            
        return True
        
    except FileNotFoundError:
        print("❌ railway.toml не найден")
        return False

def check_dockerfiles():
    """Проверяем Dockerfile'ы"""
    print_section("Проверка Dockerfile'ов")
    
    # Проверяем backend Dockerfile
    try:
        with open("Dockerfile.prod", "r") as f:
            content = f.read()
            
        if "python:" in content:
            print("✅ Dockerfile.prod использует Python")
        else:
            print("❌ Dockerfile.prod не использует Python")
            
        if "requirements.txt" in content:
            print("✅ Dockerfile.prod устанавливает зависимости")
        else:
            print("❌ Dockerfile.prod не устанавливает requirements.txt")
            
        if "${PORT" in content or "$PORT" in content:
            print("✅ Dockerfile.prod использует переменную PORT")
        else:
            print("❌ Dockerfile.prod не использует переменную PORT")
            
    except FileNotFoundError:
        print("❌ Dockerfile.prod не найден")
        return False
    
    # Проверяем frontend Dockerfile
    try:
        with open("frontend/Dockerfile.railway", "r") as f:
            content = f.read()
            
        if "node:" in content:
            print("✅ Dockerfile.railway использует Node.js")
        else:
            print("❌ Dockerfile.railway не использует Node.js")
            
        if "npm run build" in content:
            print("✅ Dockerfile.railway собирает приложение")
        else:
            print("❌ Dockerfile.railway не собирает приложение")
            
        if "serve" in content:
            print("✅ Dockerfile.railway использует serve для статики")
        else:
            print("❌ Dockerfile.railway не использует serve")
            
    except FileNotFoundError:
        print("❌ frontend/Dockerfile.railway не найден")
        return False
    
    return True

def check_environment_variables():
    """Проверяем переменные окружения"""
    print_section("Проверка переменных окружения")
    
    print("📝 Убедитесь, что в Railway настроены следующие переменные:")
    print()
    
    required_vars = [
        ("DATABASE_URL", "PostgreSQL connection string"),
        ("SECRET_KEY", "Secret key for JWT tokens"),
        ("ENVIRONMENT", "production"),
        ("SCRAPERAPI_KEY", "ScraperAPI key for web scraping"),
    ]
    
    optional_vars = [
        ("TELEGRAM_BOT_TOKEN", "Telegram bot token"),
        ("SENTRY_DSN", "Sentry error tracking"),
        ("REDIS_URL", "Redis connection string"),
    ]
    
    print("🔴 Обязательные переменные:")
    for var, description in required_vars:
        print(f"   {var} - {description}")
    
    print("\n🟡 Опциональные переменные:")
    for var, description in optional_vars:
        print(f"   {var} - {description}")
    
    print("\n💡 Настройте эти переменные в Railway Dashboard для каждого сервиса")
    
    return True

def check_git_status():
    """Проверяем статус git"""
    print_section("Проверка Git статуса")
    
    import subprocess
    
    try:
        # Проверяем статус
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️  Есть незакоммиченные изменения:")
                print(result.stdout)
                print("Рекомендуется сделать коммит перед деплоем")
            else:
                print("✅ Все изменения закоммичены")
                
            # Проверяем текущую ветку
            result = subprocess.run(["git", "branch", "--show-current"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                branch = result.stdout.strip()
                print(f"📍 Текущая ветка: {branch}")
                if branch != "main":
                    print("⚠️  Вы не на ветке main. Railway деплоит с main")
            
            return True
        else:
            print("❌ Ошибка проверки git статуса")
            return False
            
    except FileNotFoundError:
        print("❌ Git не найден")
        return False

def main():
    print("🚀 Проверка готовности к деплою в Railway")
    print("=" * 60)
    
    checks = [
        ("Файлы", check_files),
        ("Railway конфигурация", check_railway_config),
        ("Dockerfile'ы", check_dockerfiles),
        ("Переменные окружения", check_environment_variables),
        ("Git статус", check_git_status),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Ошибка при проверке {name}: {e}")
            results.append((name, False))
    
    print_section("Результаты проверки")
    
    all_passed = True
    for name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ ОШИБКА"
        print(f"{name}: {status}")
        if not result:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 Все проверки пройдены! Готово к деплою в Railway")
        print()
        print("📋 Следующие шаги:")
        print("1. Убедитесь что переменные окружения настроены в Railway")
        print("2. Сделайте push в main ветку: git push origin main")
        print("3. Railway автоматически задеплоит изменения")
        print("4. Проверьте логи деплоя в Railway Dashboard")
        return 0
    else:
        print("❌ Есть проблемы, которые нужно исправить перед деплоем")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 