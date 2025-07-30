#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram-бот для мониторинга Raspberry Pi
Показывает температуру, загрузку CPU и память
"""

import os
import sys
import time
import subprocess
import platform
from datetime import datetime
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Замените на ваш токен
ALLOWED_USERS = []  # Список разрешенных пользователей (ID из Telegram)

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
    """Получает статус системы"""
    status = {}
    
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
    except Exception as e:
        status['temperature'] = "Недоступно"
        status['temp_status'] = f"❌ Ошибка: {e}"
    
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
                
    except Exception as e:
        status['cpu_load_1'] = "Недоступно"
        status['cpu_status'] = f"❌ Ошибка: {e}"
    
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
                
    except Exception as e:
        status['memory_usage'] = "Недоступно"
        status['memory_status'] = f"❌ Ошибка: {e}"
    
    # Время работы системы
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.read().split()[0])
            
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        
        status['uptime'] = f"{days}д {hours}ч {minutes}м"
        
    except Exception as e:
        status['uptime'] = "Недоступно"
    
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
                else:
                    status['disk_usage'] = "Недоступно"
                    status['disk_status'] = "❌ Ошибка парсинга"
            else:
                status['disk_usage'] = "Недоступно"
                status['disk_status'] = "❌ Нет данных"
        else:
            status['disk_usage'] = "Недоступно"
            status['disk_status'] = f"❌ Ошибка: {stderr}"
    except Exception as e:
        status['disk_usage'] = "Недоступно"
        status['disk_status'] = f"❌ Ошибка: {e}"
    
    return status

def format_status_message(status):
    """Форматирует статус в читаемое сообщение"""
    message = "🖥️ <b>Статус Raspberry Pi</b>\n\n"
    
    # Температура
    message += f"🌡️ <b>Температура CPU:</b> {status['temperature']}\n"
    message += f"   {status['temp_status']}\n\n"
    
    # Загрузка CPU
    message += f"⚡ <b>Загрузка CPU:</b>\n"
    message += f"   1 мин: {status['cpu_load_1']}\n"
    message += f"   5 мин: {status['cpu_load_5']}\n"
    message += f"   15 мин: {status['cpu_load_15']}\n"
    message += f"   {status['cpu_status']}\n\n"
    
    # Память
    message += f"🧠 <b>Память:</b>\n"
    message += f"   Всего: {status['memory_total']}\n"
    message += f"   Используется: {status['memory_used']} ({status['memory_usage']})\n"
    message += f"   Доступно: {status['memory_available']}\n"
    message += f"   {status['memory_status']}\n\n"
    
    # Диск
    message += f"💾 <b>Диск:</b>\n"
    message += f"   Использование: {status['disk_usage']}\n"
    message += f"   Свободно: {status['disk_available']}\n"
    message += f"   {status['disk_status']}\n\n"
    
    # Время работы
    message += f"⏰ <b>Время работы:</b> {status['uptime']}\n\n"
    
    # Время обновления
    message += f"🕐 <i>Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</i>"
    
    return message

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user_id = update.effective_user.id
    
    # Проверка разрешенных пользователей (если список не пустой)
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return
    
    welcome_message = (
        "🤖 <b>Raspberry Pi Monitor Bot</b>\n\n"
        "Доступные команды:\n"
        "/status - Показать статус системы\n"
        "/help - Показать эту справку\n\n"
        "Используйте /status для получения информации о температуре, "
        "загрузке CPU и памяти."
    )
    
    await update.message.reply_text(welcome_message, parse_mode='HTML')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /status"""
    user_id = update.effective_user.id
    
    # Проверка разрешенных пользователей (если список не пустой)
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return
    
    # Отправляем сообщение о начале получения данных
    status_message = await update.message.reply_text("📊 Получаю данные о системе...")
    
    try:
        # Получаем статус системы
        system_status = get_system_status()
        
        # Форматируем сообщение
        formatted_message = format_status_message(system_status)
        
        # Обновляем сообщение
        await status_message.edit_text(formatted_message, parse_mode='HTML')
        
    except Exception as e:
        error_message = f"❌ Ошибка при получении статуса: {e}"
        await status_message.edit_text(error_message)
        logger.error(f"Error getting status: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    user_id = update.effective_user.id
    
    # Проверка разрешенных пользователей (если список не пустой)
    if ALLOWED_USERS and user_id not in ALLOWED_USERS:
        await update.message.reply_text("❌ У вас нет доступа к этому боту.")
        return
    
    help_text = (
        "🤖 <b>Raspberry Pi Monitor Bot - Справка</b>\n\n"
        "<b>Команды:</b>\n"
        "/start - Запустить бота\n"
        "/status - Показать статус системы\n"
        "/help - Показать эту справку\n\n"
        "<b>Что показывает /status:</b>\n"
        "• Температура CPU\n"
        "• Загрузка процессора (1, 5, 15 минут)\n"
        "• Использование памяти\n"
        "• Свободное место на диске\n"
        "• Время работы системы\n\n"
        "<b>Статусы:</b>\n"
        "✅ - Нормальное состояние\n"
        "⚠ - Повышенные показатели\n"
        "❌ - Критические показатели\n\n"
        "<i>Бот обновляется в реальном времени при каждом запросе.</i>"
    )
    
    await update.message.reply_text(help_text, parse_mode='HTML')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    """Основная функция"""
    # Проверяем токен
    if TELEGRAM_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Ошибка: Не установлен токен бота!")
        print("1. Получите токен у @BotFather в Telegram")
        print("2. Замените 'YOUR_BOT_TOKEN_HERE' на ваш токен в файле")
        return
    
    print("🚀 Запуск Telegram-бота для мониторинга Raspberry Pi...")
    
    # Создаем приложение
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Добавляем обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("help", help_command))
    
    # Добавляем обработчик ошибок
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    print("✅ Бот запущен! Нажмите Ctrl+C для остановки.")
    application.run_polling()

if __name__ == "__main__":
    main() 