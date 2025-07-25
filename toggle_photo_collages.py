#!/usr/bin/env python3
"""
Скрипт для управления настройкой коллажей фотографий
"""
import os
import sys
from pathlib import Path

def update_env_setting(key: str, value: str):
    """Обновляет или добавляет переменную в .env файл"""
    env_path = Path('.env')
    
    if not env_path.exists():
        print("❌ Файл .env не найден")
        return False
    
    # Читаем содержимое
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Ищем существующую настройку
    key_found = False
    for i, line in enumerate(lines):
        if line.strip().startswith(f"{key}="):
            lines[i] = f"{key}={value}\n"
            key_found = True
            break
    
    # Если не найдена, добавляем в конец
    if not key_found:
        lines.append(f"\n{key}={value}\n")
    
    # Записываем обратно
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    return True

def get_current_setting(key: str) -> str:
    """Получает текущее значение переменной из .env"""
    env_path = Path('.env')
    
    if not env_path.exists():
        return "не найден"
    
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip().startswith(f"{key}="):
                return line.split('=', 1)[1].strip()
    
    return "не установлено"

def main():
    if len(sys.argv) < 2:
        print("🎨 Управление коллажами фотографий")
        print("")
        print("Использование:")
        print("  python toggle_photo_collages.py <command>")
        print("")
        print("Команды:")
        print("  on      - включить коллажи")
        print("  off     - выключить коллажи") 
        print("  status  - показать текущий статус")
        print("")
        return
    
    command = sys.argv[1].lower()
    
    if command == "status":
        current = get_current_setting("ENABLE_PHOTO_COLLAGES")
        print(f"📊 Текущий статус коллажей: {current}")
        
        if current.lower() in ['true', '1', 'yes', 'on']:
            print("✅ Коллажи ВКЛЮЧЕНЫ")
        else:
            print("❌ Коллажи ВЫКЛЮЧЕНЫ")
    
    elif command == "on":
        if update_env_setting("ENABLE_PHOTO_COLLAGES", "true"):
            print("✅ Коллажи ВКЛЮЧЕНЫ")
            print("📝 Переменная ENABLE_PHOTO_COLLAGES=true установлена в .env")
            print("")
            print("🔑 Для реального создания коллажей нужны API ключи:")
            print("   HTMLCSS_USER_ID=your_user_id")
            print("   HTMLCSS_API_KEY=your_api_key")
            print("   Регистрация: https://htmlcsstoimage.com/")
        else:
            print("❌ Ошибка обновления .env файла")
    
    elif command == "off":
        if update_env_setting("ENABLE_PHOTO_COLLAGES", "false"):
            print("❌ Коллажи ВЫКЛЮЧЕНЫ")
            print("📝 Переменная ENABLE_PHOTO_COLLAGES=false установлена в .env")
        else:
            print("❌ Ошибка обновления .env файла")
    
    else:
        print(f"❌ Неизвестная команда: {command}")
        print("Используйте: on, off, или status")

if __name__ == "__main__":
    main() 