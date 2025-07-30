Данный проект содержит тестовые скрипты для проверки функциональности Raspberry Pi 3 и Telegram-бота для мониторинга.

## 📁 Файлы

- `system_test.py` — Полный тест системы Raspberry Pi 3
- `telegram_monitor_bot.py` — Telegram-бот для мониторинга Raspberry Pi
- `config.py` — Конфигурация токена Telegram-бота
- `TELEGRAM_BOT_SETUP.md` — Инструкция по настройке Telegram-бота
- `README.md` — Этот файл с инструкциями

## 🚀 Запуск Telegram-бота для мониторинга

### Установка зависимостей

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
sudo apt-get install python3-telegram-bot
```

**Если нужен pip (например, для виртуального окружения):**

```bash
sudo apt-get install python3-venv
python3 -m venv ~/telegram_bot_env
source ~/telegram_bot_env/bin/activate
pip install python-telegram-bot
```

### Настройка токена

1. Откройте файл `config.py`
2. Впишите ваш токен:
   ```python
   BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```

### Запуск бота

```bash
python telegram_monitor_bot.py
```

**Подробная инструкция по настройке:** `TELEGRAM_BOT_SETUP.md`

## 📝 Интерпретация результатов

### Символы статуса
- ✅ **Успешно** — функция работает корректно
- ⚠ **Предупреждение** — есть проблемы, но не критичные
- ❌ **Ошибка** — критическая проблема

### Температура CPU
- < 50°C: ✅ Нормальная температура
- 50-70°C: ⚠ Повышенная температура
- > 70°C: ❌ Критическая температура

### Использование памяти
- < 80%: ✅ Нормальное использование
- > 80%: ⚠ Высокое использование

### Использование диска
- < 90%: ✅ Достаточно места
- > 90%: ⚠ Мало места

## 📈 Мониторинг

Для регулярного мониторинга можно добавить скрипты в cron:

```bash
# Редактирование crontab
crontab -e

# Запуск теста каждые 6 часов
0 */6 * * * /usr/bin/python3 /path/to/system_test.py >> /var/log/pi_test.log 2>&1
```

## 🤝 Вклад в проект

При обнаружении проблем или предложениях по улучшению создавайте issues в репозитории.

## 📄 Лицензия

Этот проект распространяется под лицензией MIT.