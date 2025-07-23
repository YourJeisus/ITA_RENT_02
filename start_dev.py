#!/usr/bin/env python3
"""
Скрипт для запуска всего проекта в режиме разработки
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def check_requirements():
    """Проверяем наличие необходимых зависимостей"""
    print_section("Проверка зависимостей")
    
    # Проверяем Python пакеты
    try:
        import uvicorn
        import fastapi
        import sqlalchemy
        print("✅ Python зависимости установлены")
    except ImportError as e:
        print(f"❌ Отсутствуют Python зависимости: {e}")
        print("Установите зависимости: pip install -r requirements.txt")
        return False
    
    # Проверяем Node.js
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js установлен: {result.stdout.strip()}")
        else:
            print("❌ Node.js не найден")
            return False
    except FileNotFoundError:
        print("❌ Node.js не установлен")
        return False
    
    # Проверяем npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm установлен: {result.stdout.strip()}")
        else:
            print("❌ npm не найден")
            return False
    except FileNotFoundError:
        print("❌ npm не установлен")
        return False
    
    return True

def setup_database():
    """Настройка базы данных"""
    print_section("Настройка базы данных")
    
    try:
        # Применяем миграции
        print("Применение миграций...")
        result = subprocess.run(["alembic", "upgrade", "head"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Миграции применены успешно")
        else:
            print(f"❌ Ошибка применения миграций: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ Alembic не найден")
        return False
    
    return True

def install_frontend_deps():
    """Установка зависимостей фронтенда"""
    print_section("Установка зависимостей фронтенда")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Папка frontend не найдена")
        return False
    
    try:
        os.chdir(frontend_path)
        
        # Проверяем наличие node_modules
        if not Path("node_modules").exists():
            print("Установка npm зависимостей...")
            result = subprocess.run(["npm", "install"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ npm зависимости установлены")
            else:
                print(f"❌ Ошибка установки npm зависимостей: {result.stderr}")
                return False
        else:
            print("✅ npm зависимости уже установлены")
        
        os.chdir("..")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        os.chdir("..")
        return False

def start_backend():
    """Запуск бэкенда"""
    print_section("Запуск бэкенда")
    
    try:
        print("🚀 Запуск FastAPI сервера на http://localhost:8000")
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "src.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
        return backend_process
    except Exception as e:
        print(f"❌ Ошибка запуска бэкенда: {e}")
        return None

def start_frontend():
    """Запуск фронтенда"""
    print_section("Запуск фронтенда")
    
    try:
        os.chdir("frontend")
        print("🚀 Запуск React сервера на http://localhost:5173")
        frontend_process = subprocess.Popen([
            "npm", "run", "dev"
        ])
        os.chdir("..")
        return frontend_process
    except Exception as e:
        print(f"❌ Ошибка запуска фронтенда: {e}")
        os.chdir("..")
        return None

def wait_for_services():
    """Ожидание запуска сервисов"""
    print_section("Ожидание запуска сервисов")
    
    import requests
    
    # Ждем бэкенд
    print("Ожидание запуска бэкенда...")
    for i in range(30):  # 30 секунд
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Бэкенд запущен и отвечает")
                break
        except:
            pass
        time.sleep(1)
        print(f"  Попытка {i+1}/30...")
    else:
        print("❌ Бэкенд не запустился в течение 30 секунд")
        return False
    
    # Ждем фронтенд
    print("Ожидание запуска фронтенда...")
    for i in range(30):  # 30 секунд
        try:
            response = requests.get("http://localhost:5173", timeout=2)
            if response.status_code == 200:
                print("✅ Фронтенд запущен и отвечает")
                break
        except:
            pass
        time.sleep(1)
        print(f"  Попытка {i+1}/30...")
    else:
        print("❌ Фронтенд не запустился в течение 30 секунд")
        return False
    
    return True

def main():
    print("🚀 ITA_RENT_BOT - Запуск в режиме разработки")
    print("=" * 60)
    
    # Проверяем зависимости
    if not check_requirements():
        print("\n❌ Не все зависимости установлены. Завершение.")
        return 1
    
    # Настраиваем базу данных
    if not setup_database():
        print("\n❌ Ошибка настройки базы данных. Завершение.")
        return 1
    
    # Устанавливаем зависимости фронтенда
    if not install_frontend_deps():
        print("\n❌ Ошибка установки зависимостей фронтенда. Завершение.")
        return 1
    
    # Запускаем сервисы
    backend_process = start_backend()
    if not backend_process:
        return 1
    
    time.sleep(3)  # Даем бэкенду время запуститься
    
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return 1
    
    # Ждем запуска сервисов
    if not wait_for_services():
        backend_process.terminate()
        frontend_process.terminate()
        return 1
    
    print_section("🎉 Все сервисы запущены!")
    print("📱 Фронтенд: http://localhost:5173")
    print("🔧 API: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("\n💡 Для остановки нажмите Ctrl+C")
    
    # Обработка сигнала остановки
    def signal_handler(sig, frame):
        print_section("Остановка сервисов")
        print("Остановка бэкенда...")
        backend_process.terminate()
        print("Остановка фронтенда...")
        frontend_process.terminate()
        
        # Ждем завершения процессов
        backend_process.wait()
        frontend_process.wait()
        
        print("✅ Все сервисы остановлены")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # Ждем завершения процессов
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 