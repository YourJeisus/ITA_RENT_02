#!/usr/bin/env python3
"""
Скрипт проверки готовности к деплою на Railway
"""

import os
import json
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Проверка существования файла"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} НЕ НАЙДЕН: {filepath}")
        return False

def check_railway_config():
    """Проверка конфигурации Railway"""
    print("🚂 Проверка конфигурации Railway:")
    
    if not check_file_exists("railway.toml", "Railway конфигурация"):
        return False
    
    # Проверяем содержимое railway.toml
    try:
        with open("railway.toml", "r") as f:
            content = f.read()
            
        if "[[services]]" in content and "name = \"backend\"" in content and "name = \"frontend\"" in content:
            print("✅ Railway конфигурация содержит оба сервиса (backend и frontend)")
        else:
            print("❌ Railway конфигурация не содержит правильные сервисы")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения railway.toml: {e}")
        return False
    
    return True

def check_dockerfiles():
    """Проверка Dockerfile файлов"""
    print("\n📦 Проверка Dockerfile файлов:")
    
    all_good = True
    all_good &= check_file_exists("Dockerfile.prod", "Backend Production Dockerfile")
    all_good &= check_file_exists("frontend/Dockerfile.railway", "Frontend Railway Dockerfile")
    
    return all_good

def check_frontend_package():
    """Проверка package.json frontend"""
    print("\n⚛️ Проверка frontend:")
    
    if not check_file_exists("frontend/package.json", "Frontend package.json"):
        return False
    
    try:
        with open("frontend/package.json", "r") as f:
            package = json.load(f)
        
        if "build" in package.get("scripts", {}):
            print("✅ Frontend содержит build script")
        else:
            print("❌ Frontend НЕ содержит build script")
            return False
            
        if "vite" in package.get("devDependencies", {}):
            print("✅ Frontend использует Vite")
        else:
            print("❌ Frontend НЕ использует Vite")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения package.json: {e}")
        return False
    
    return True

def check_python_requirements():
    """Проверка Python requirements"""
    print("\n🐍 Проверка Python requirements:")
    
    if not check_file_exists("requirements.txt", "Python requirements"):
        return False
    
    try:
        with open("requirements.txt", "r") as f:
            requirements = f.read()
        
        required_packages = ["fastapi", "uvicorn", "python-dotenv"]
        missing_packages = []
        
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
            return False
        else:
            print("✅ Все необходимые пакеты присутствуют")
            
    except Exception as e:
        print(f"❌ Ошибка чтения requirements.txt: {e}")
        return False
    
    return True

def check_cors_config():
    """Проверка CORS конфигурации"""
    print("\n🌐 Проверка CORS конфигурации:")
    
    if not check_file_exists("src/main.py", "Backend main.py"):
        return False
    
    try:
        with open("src/main.py", "r") as f:
            content = f.read()
        
        if "allow_origin_regex" in content and "railway" in content:
            print("✅ CORS настроен для Railway доменов")
        else:
            print("❌ CORS НЕ настроен для Railway доменов")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка чтения main.py: {e}")
        return False
    
    return True

def check_git_status():
    """Проверка Git статуса"""
    print("\n📝 Проверка Git статуса:")
    
    # Проверяем есть ли git
    if not os.path.exists(".git"):
        print("❌ Git репозиторий не инициализирован")
        return False
    
    print("✅ Git репозиторий найден")
    print("ℹ️  Убедитесь, что все изменения закоммичены и запушены!")
    
    return True

def print_deployment_checklist():
    """Печать чеклиста для деплоя"""
    print("\n" + "="*60)
    print("📋 ЧЕКЛИСТ ДЛЯ ДЕПЛОЯ НА RAILWAY")
    print("="*60)
    print()
    print("1. 🚂 Зайдите на https://railway.app")
    print("2. 📁 Создайте новый проект из GitHub репозитория")
    print("3. 🔧 Railway автоматически создаст 2 сервиса:")
    print("   • backend (FastAPI)")
    print("   • frontend (React)")
    print()
    print("4. ⚙️ Настройте переменные окружения для backend:")
    print("   • ENVIRONMENT=production")
    print("   • SECRET_KEY=your-secret-key")
    print("   • DATABASE_URL=${{Postgres.DATABASE_URL}}")
    print()
    print("5. 🗄️ Добавьте PostgreSQL базу данных:")
    print("   • New → Database → Add PostgreSQL")
    print()
    print("6. 🌐 Настройте переменные для frontend:")
    print("   • VITE_API_URL=https://your-backend.railway.app")
    print()
    print("7. ✅ Проверьте деплой:")
    print("   • Backend: /health endpoint")
    print("   • Frontend: главная страница")
    print()
    print("📖 Подробная инструкция: RAILWAY_DEPLOYMENT.md")
    print()

def main():
    print("🔍 Проверка готовности к деплою на Railway\n")
    
    all_checks = [
        check_railway_config(),
        check_dockerfiles(),
        check_frontend_package(),
        check_python_requirements(),
        check_cors_config(),
        check_git_status()
    ]
    
    if all(all_checks):
        print("\n" + "="*50)
        print("🎉 ВСЕ ПРОВЕРКИ ПРОШЛИ УСПЕШНО!")
        print("✅ Готово к деплою на Railway!")
        print_deployment_checklist()
        return 0
    else:
        print("\n" + "="*50)
        print("❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ!")
        print("Исправьте указанные выше ошибки перед деплоем.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 