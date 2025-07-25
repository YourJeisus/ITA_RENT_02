#!/usr/bin/env python3
"""
Скрипт для переключения режима отладки уведомлений
Изменяет переменную DEBUG_NOTIFICATIONS в .env файле
"""
import os
import sys
from pathlib import Path

def read_env_file():
    """Читает содержимое .env файла"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Файл .env не найден!")
        return None
    
    with open(env_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def write_env_file(lines):
    """Записывает содержимое в .env файл"""
    env_path = Path(".env")
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

def toggle_debug_mode():
    """Переключает режим отладки"""
    lines = read_env_file()
    if lines is None:
        return False
    
    # Ищем строку с DEBUG_NOTIFICATIONS
    debug_line_index = None
    current_value = "false"
    
    for i, line in enumerate(lines):
        if line.strip().startswith("DEBUG_NOTIFICATIONS="):
            debug_line_index = i
            current_value = line.strip().split("=")[1].lower()
            break
    
    # Определяем новое значение (Pydantic использует булевые значения)
    new_value = "false" if current_value.lower() in ["true", "1", "yes"] else "true"
    new_line = f"DEBUG_NOTIFICATIONS={new_value}\n"
    
    if debug_line_index is not None:
        # Обновляем существующую строку
        lines[debug_line_index] = new_line
    else:
        # Добавляем новую строку в конец файла
        if lines and not lines[-1].endswith('\n'):
            lines.append('\n')
        lines.append(new_line)
    
    # Записываем обратно в файл
    write_env_file(lines)
    
    print(f"✅ Режим отладки уведомлений: {new_value.upper()}")
    
    if new_value == "true":
        print("🐛 ВКЛЮЧЕН режим отладки:")
        print("   - Временные ограничения отключены")
        print("   - Интервал: 60 секунд")
        print("   - Отправка дубликатов включена")
        print("   - Подробные логи")
    else:
        print("✅ ВЫКЛЮЧЕН режим отладки:")
        print("   - Обычные временные ограничения")
        print("   - Интервал: 30 минут")
        print("   - Защита от дубликатов")
        print("   - Стандартные логи")
    
    print("\n💡 Перезапустите контейнер для применения изменений:")
    print("   docker-compose restart notification-worker")
    
    return True

def show_current_status():
    """Показывает текущий статус режима отладки"""
    lines = read_env_file()
    if lines is None:
        return
    
    current_value = "false"  # по умолчанию
    
    for line in lines:
        if line.strip().startswith("DEBUG_NOTIFICATIONS="):
            current_value = line.strip().split("=")[1].lower()
            break
    
    print(f"📊 Текущий режим отладки уведомлений: {current_value.upper()}")
    
    if current_value == "true":
        print("🐛 Режим отладки ВКЛЮЧЕН")
    else:
        print("✅ Обычный режим")

def main():
    """Главная функция"""
    if len(sys.argv) > 1:
        action = sys.argv[1].lower()
        
        if action in ['status', 's']:
            show_current_status()
        elif action in ['on', 'enable', 'true']:
            # Принудительно включаем
            lines = read_env_file()
            if lines is None:
                return
                
            debug_line_index = None
            for i, line in enumerate(lines):
                if line.strip().startswith("DEBUG_NOTIFICATIONS="):
                    debug_line_index = i
                    break
            
            new_line = "DEBUG_NOTIFICATIONS=true\n"
            if debug_line_index is not None:
                lines[debug_line_index] = new_line
            else:
                if lines and not lines[-1].endswith('\n'):
                    lines.append('\n')
                lines.append(new_line)
            
            write_env_file(lines)
            print("🐛 Режим отладки уведомлений ПРИНУДИТЕЛЬНО ВКЛЮЧЕН")
            
        elif action in ['off', 'disable', 'false']:
            # Принудительно выключаем
            lines = read_env_file()
            if lines is None:
                return
                
            debug_line_index = None
            for i, line in enumerate(lines):
                if line.strip().startswith("DEBUG_NOTIFICATIONS="):
                    debug_line_index = i
                    break
            
            new_line = "DEBUG_NOTIFICATIONS=false\n"
            if debug_line_index is not None:
                lines[debug_line_index] = new_line
            else:
                if lines and not lines[-1].endswith('\n'):
                    lines.append('\n')
                lines.append(new_line)
            
            write_env_file(lines)
            print("✅ Режим отладки уведомлений ПРИНУДИТЕЛЬНО ВЫКЛЮЧЕН")
            
        else:
            print(f"❌ Неизвестное действие: {action}")
            print("Доступные действия: on, off, status, toggle")
    else:
        # Переключение режима
        toggle_debug_mode()

if __name__ == "__main__":
    main() 