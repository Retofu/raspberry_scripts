#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Быстрый тест функций мониторинга Raspberry Pi
Используется для проверки работы функций перед настройкой Telegram-бота
"""

import os
import sys
import time
import subprocess
from datetime import datetime

def run_command(command):
    """Выполняет команду и возвращает результат"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Команда превысила время выполнения", 1
    except Exception as e:
        return "", f"Ошибка выполнения команды: {e}", 1

def get_system_status():
    """Получает статус системы (та же функция, что и в Telegram-боте)"""
    status = {}
    
    print("📊 Получение данных о системе...")
    
    # Температура CPU
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000.0
            status['temperature'] = f"{temp:.1f}°C"
            
            if temp < 50:
                status['temp_status'] = "✅ Нормальная"
            elif temp < 70:
                status['temp_status'] = "⚠ Повышенная"
            else:
                status['temp_status'] = "❌ Критическая!"
        print(f"✓ Температура: {status['temperature']} - {status['temp_status']}")
    except Exception as e:
        status['temperature'] = "Недоступно"
        status['temp_status'] = f"❌ Ошибка: {e}"
        print(f"❌ Ошибка получения температуры: {e}")
    
    # Загрузка CPU
    try:
        with open('/proc/loadavg', 'r') as f:
            load = f.read().strip().split()
            status['cpu_load_1'] = load[0]
            status['cpu_load_5'] = load[1]
            status['cpu_load_15'] = load[2]
            
            # Получаем количество ядер
            with open('/proc/cpuinfo', 'r') as cpuinfo:
                cores = cpuinfo.read().count('processor')
            
            load_1_float = float(load[0])
            if load_1_float < cores * 0.7:
                status['cpu_status'] = "✅ Нормальная"
            elif load_1_float < cores * 1.5:
                status['cpu_status'] = "⚠ Повышенная"
            else:
                status['cpu_status'] = "❌ Высокая"
        print(f"✓ CPU: 1м={status['cpu_load_1']}, 5м={status['cpu_load_5']}, 15м={status['cpu_load_15']} - {status['cpu_status']}")
    except Exception as e:
        status['cpu_load_1'] = "Недоступно"
        status['cpu_status'] = f"❌ Ошибка: {e}"
        print(f"❌ Ошибка получения загрузки CPU: {e}")
    
    # Память
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            lines = meminfo.split('\n')
            
            total_mem = 0
            available_mem = 0
            
            for line in lines:
                if line.startswith('MemTotal:'):
                    total_mem = int(line.split()[1])
                elif line.startswith('MemAvailable:'):
                    available_mem = int(line.split()[1])
            
            used_mem = total_mem - available_mem
            usage_percent = (used_mem / total_mem) * 100
            
            status['memory_total'] = f"{total_mem / 1024 / 1024:.1f} GB"
            status['memory_used'] = f"{used_mem / 1024 / 1024:.1f} GB"
            status['memory_available'] = f"{available_mem / 1024 / 1024:.1f} GB"
            status['memory_usage'] = f"{usage_percent:.1f}%"
            
            if usage_percent < 80:
                status['memory_status'] = "✅ Нормальное"
            else:
                status['memory_status'] = "⚠ Высокое"
        print(f"✓ Память: {status['memory_used']}/{status['memory_total']} ({status['memory_usage']}) - {status['memory_status']}")
    except Exception as e:
        status['memory_usage'] = "Недоступно"
        status['memory_status'] = f"❌ Ошибка: {e}"
        print(f"❌ Ошибка получения информации о памяти: {e}")
    
    # Время работы системы
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
            
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        status['uptime'] = f"{days}д {hours}ч {minutes}м"
        print(f"✓ Время работы: {status['uptime']}")
    except Exception as e:
        status['uptime'] = "Недоступно"
        print(f"❌ Ошибка получения времени работы: {e}")
    
    # Свободное место на диске
    try:
        stdout, stderr, returncode = run_command("df -h /")
        if returncode == 0:
            lines = stdout.split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                if len(parts) >= 5:
                    status['disk_usage'] = parts[4].rstrip('%')
                    status['disk_available'] = parts[3]
                    
                    usage = int(status['disk_usage'])
                    if usage < 90:
                        status['disk_status'] = "✅ Достаточно"
                    else:
                        status['disk_status'] = "⚠ Мало места"
                    print(f"✓ Диск: {status['disk_usage']} использовано, {status['disk_available']} свободно - {status['disk_status']}")
                else:
                    status['disk_usage'] = "Недоступно"
                    status['disk_status'] = "❌ Ошибка парсинга"
                    print("❌ Ошибка парсинга информации о диске")
            else:
                status['disk_usage'] = "Недоступно"
                status['disk_status'] = "❌ Нет данных"
                print("❌ Нет данных о диске")
        else:
            status['disk_usage'] = "Недоступно"
            status['disk_status'] = f"❌ Ошибка: {stderr}"
            print(f"❌ Ошибка получения информации о диске: {stderr}")
    except Exception as e:
        status['disk_usage'] = "Недоступно"
        status['disk_status'] = f"❌ Ошибка: {e}"
        print(f"❌ Ошибка получения информации о диске: {e}")
    
    return status

def format_status_message(status):
    """Форматирует статус в читаемое сообщение (та же функция, что и в Telegram-боте)"""
    message = "🖥️ Статус Raspberry Pi\n\n"
    
    # Температура
    message += f"🌡️ Температура CPU: {status['temperature']}\n"
    message += f"   {status['temp_status']}\n\n"
    
    # Загрузка CPU
    message += f"⚡ Загрузка CPU:\n"
    message += f"   1 мин: {status['cpu_load_1']}\n"
    message += f"   5 мин: {status['cpu_load_5']}\n"
    message += f"   15 мин: {status['cpu_load_15']}\n"
    message += f"   {status['cpu_status']}\n\n"
    
    # Память
    message += f"🧠 Память:\n"
    message += f"   Всего: {status['memory_total']}\n"
    message += f"   Используется: {status['memory_used']} ({status['memory_usage']})\n"
    message += f"   Доступно: {status['memory_available']}\n"
    message += f"   {status['memory_status']}\n\n"
    
    # Диск
    message += f"💾 Диск:\n"
    message += f"   Использование: {status['disk_usage']}\n"
    message += f"   Свободно: {status['disk_available']}\n"
    message += f"   {status['disk_status']}\n\n"
    
    # Время работы
    message += f"⏰ Время работы: {status['uptime']}\n\n"
    
    # Время обновления
    message += f"🕐 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    
    return message

def test_telegram_library():
    """Проверяет доступность библиотеки Telegram"""
    print("\n🔍 Проверка библиотеки Telegram...")
    try:
        import telegram
        print("✓ Библиотека python-telegram-bot доступна")
        print(f"  Версия: {telegram.__version__}")
        return True
    except ImportError:
        print("❌ Библиотека python-telegram-bot не установлена")
        print("  Установите: pip3 install python-telegram-bot")
        return False

def main():
    """Основная функция"""
    print("🚀 БЫСТРЫЙ ТЕСТ ФУНКЦИЙ МОНИТОРИНГА")
    print("=" * 50)
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    
    try:
        # Тестируем функции мониторинга
        system_status = get_system_status()
        
        print("\n" + "=" * 50)
        print("ФОРМАТИРОВАННОЕ СООБЩЕНИЕ:")
        print("=" * 50)
        
        # Показываем, как будет выглядеть сообщение в Telegram
        formatted_message = format_status_message(system_status)
        print(formatted_message)
        
        # Проверяем библиотеку Telegram
        telegram_available = test_telegram_library()
        
        print("\n" + "=" * 50)
        print("РЕЗУЛЬТАТ ТЕСТИРОВАНИЯ")
        print("=" * 50)
        
        if telegram_available:
            print("✅ Все готово для запуска Telegram-бота!")
            print("📝 Следующие шаги:")
            print("1. Получите токен у @BotFather")
            print("2. Замените токен в telegram_monitor_bot.py")
            print("3. Запустите: python3 telegram_monitor_bot.py")
        else:
            print("⚠ Установите библиотеку Telegram для полной функциональности")
            print("  pip3 install python-telegram-bot")
        
        print(f"\n🕐 Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 