#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для Raspberry Pi 3
Проверяет базовую функциональность системы
"""

import os
import sys
import time
import subprocess
import platform
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

def get_system_info():
    """Получает информацию о системе"""
    print("=" * 50)
    print("ИНФОРМАЦИЯ О СИСТЕМЕ")
    print("=" * 50)
    
    # Информация о платформе
    print(f"Платформа: {platform.platform()}")
    print(f"Архитектура: {platform.machine()}")
    print(f"Процессор: {platform.processor()}")
    print(f"Python версия: {sys.version}")
    
    # Информация о Raspberry Pi
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
            if 'Raspberry Pi' in cpuinfo:
                print("✓ Обнаружена Raspberry Pi")
            else:
                print("⚠ Система не похожа на Raspberry Pi")
    except FileNotFoundError:
        print("⚠ Не удалось прочитать информацию о CPU")

def get_cpu_temperature():
    """Получает температуру CPU"""
    print("\n" + "=" * 50)
    print("ТЕМПЕРАТУРА CPU")
    print("=" * 50)
    
    try:
        with open('/sys/class/thermal/thermal_zone0/temp', 'r') as f:
            temp = int(f.read().strip()) / 1000.0
            print(f"Температура CPU: {temp:.1f}°C")
            
            if temp < 50:
                print("✓ Температура в норме")
            elif temp < 70:
                print("⚠ Температура повышена")
            else:
                print("❌ Температура критическая!")
    except FileNotFoundError:
        print("⚠ Не удалось получить температуру CPU")
    except Exception as e:
        print(f"❌ Ошибка при получении температуры: {e}")

def get_memory_info():
    """Получает информацию о памяти"""
    print("\n" + "=" * 50)
    print("ИНФОРМАЦИЯ О ПАМЯТИ")
    print("=" * 50)
    
    try:
        with open('/proc/meminfo', 'r') as f:
            meminfo = f.read()
            lines = meminfo.split('\n')
            
            total_mem = 0
            free_mem = 0
            available_mem = 0
            
            for line in lines:
                if line.startswith('MemTotal:'):
                    total_mem = int(line.split()[1])
                elif line.startswith('MemFree:'):
                    free_mem = int(line.split()[1])
                elif line.startswith('MemAvailable:'):
                    available_mem = int(line.split()[1])
            
            total_gb = total_mem / 1024 / 1024
            free_gb = free_mem / 1024 / 1024
            available_gb = available_mem / 1024 / 1024
            used_gb = total_gb - available_gb
            usage_percent = (used_gb / total_gb) * 100
            
            print(f"Общая память: {total_gb:.1f} GB")
            print(f"Свободная память: {free_gb:.1f} GB")
            print(f"Доступная память: {available_gb:.1f} GB")
            print(f"Используется: {used_gb:.1f} GB ({usage_percent:.1f}%)")
            
            if usage_percent < 80:
                print("✓ Использование памяти в норме")
            else:
                print("⚠ Высокое использование памяти")
                
    except Exception as e:
        print(f"❌ Ошибка при получении информации о памяти: {e}")

def get_disk_usage():
    """Получает информацию о диске"""
    print("\n" + "=" * 50)
    print("ИНФОРМАЦИЯ О ДИСКЕ")
    print("=" * 50)
    
    stdout, stderr, returncode = run_command("df -h /")
    
    if returncode == 0:
        lines = stdout.split('\n')
        if len(lines) > 1:
            parts = lines[1].split()
            if len(parts) >= 5:
                filesystem = parts[0]
                total = parts[1]
                used = parts[2]
                available = parts[3]
                usage_percent = parts[4].rstrip('%')
                
                print(f"Файловая система: {filesystem}")
                print(f"Общий размер: {total}")
                print(f"Использовано: {used}")
                print(f"Доступно: {available}")
                print(f"Использование: {usage_percent}%")
                
                if int(usage_percent) < 90:
                    print("✓ Свободного места достаточно")
                else:
                    print("⚠ Мало свободного места!")
        else:
            print("⚠ Не удалось разобрать информацию о диске")
    else:
        print(f"❌ Ошибка при получении информации о диске: {stderr}")

def get_network_info():
    """Получает информацию о сети"""
    print("\n" + "=" * 50)
    print("СЕТЕВЫЕ ИНТЕРФЕЙСЫ")
    print("=" * 50)
    
    stdout, stderr, returncode = run_command("ip addr show")
    
    if returncode == 0:
        interfaces = []
        current_interface = None
        
        for line in stdout.split('\n'):
            if line.strip().startswith(('1:', '2:', '3:', '4:')):
                if 'lo' in line:
                    current_interface = 'lo (localhost)'
                elif 'eth' in line:
                    current_interface = 'eth0 (Ethernet)'
                elif 'wlan' in line:
                    current_interface = 'wlan0 (Wi-Fi)'
                else:
                    current_interface = line.split(':')[1].strip()
                interfaces.append(current_interface)
            elif 'inet ' in line and current_interface:
                ip = line.split()[1].split('/')[0]
                print(f"{current_interface}: {ip}")
        
        if not interfaces:
            print("⚠ Сетевые интерфейсы не найдены")
    else:
        print(f"❌ Ошибка при получении сетевой информации: {stderr}")

def get_uptime():
    """Получает время работы системы"""
    print("\n" + "=" * 50)
    print("ВРЕМЯ РАБОТЫ СИСТЕМЫ")
    print("=" * 50)
    
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
            
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        print(f"Система работает: {days} дней, {hours} часов, {minutes} минут")
        
        if days > 30:
            print("⚠ Система работает более месяца - рекомендуется перезагрузка")
        else:
            print("✓ Время работы системы в норме")
            
    except Exception as e:
        print(f"❌ Ошибка при получении времени работы: {e}")

def test_gpio_access():
    """Проверяет доступ к GPIO"""
    print("\n" + "=" * 50)
    print("ПРОВЕРКА GPIO")
    print("=" * 50)
    
    try:
        import RPi.GPIO as GPIO
        print("✓ Модуль RPi.GPIO доступен")
        
        # Проверяем, можем ли мы установить режим
        GPIO.setmode(GPIO.BCM)
        print("✓ GPIO режим установлен успешно")
        
        # Очищаем настройки
        GPIO.cleanup()
        print("✓ GPIO очищен успешно")
        
    except ImportError:
        print("⚠ Модуль RPi.GPIO не установлен")
        print("  Установите: sudo apt-get install python3-rpi.gpio")
    except Exception as e:
        print(f"❌ Ошибка при работе с GPIO: {e}")

def main():
    """Основная функция"""
    print("🚀 ЗАПУСК ТЕСТОВОГО СКРИПТА ДЛЯ RASPBERRY PI 3")
    print(f"Время запуска: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        get_system_info()
        get_cpu_temperature()
        get_memory_info()
        get_disk_usage()
        get_network_info()
        get_uptime()
        test_gpio_access()
        
        print("\n" + "=" * 50)
        print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
        print("=" * 50)
        print(f"Время завершения: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Тестирование прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main() 