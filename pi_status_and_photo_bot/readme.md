Данный проект содержит скрипты для мониторинга состояния Raspberry Pi 3 и отправки фото с подключенной по USB веб-камеры.

## 📁 Файлы

- `system_test.py` — Полный тест системы Raspberry Pi 3
- `telegram_monitor_bot.py` — Telegram-бот для мониторинга Raspberry Pi с функцией фото
- `config.py` — Конфигурация токена Telegram-бота
- `TELEGRAM_BOT_SETUP.md` — Инструкция по настройке Telegram-бота
- `README.md` — Этот файл с инструкциями

## 🚀 Запуск Telegram-бота для мониторинга

### Установка зависимостей

```bash
sudo apt-get update
sudo apt-get install python3 python3-pip
sudo apt-get install python3-telegram-bot
sudo apt-get install fswebcam
```

**Если нужен pip (например, для виртуального окружения):**

```bash
sudo apt-get install python3-venv
python3 -m venv ~/telegram_bot_env
source ~/telegram_bot_env/bin/activate
pip install python-telegram-bot
```

**Если pip3 install не работает из-за ошибки externally-managed-environment:**
- Используйте только в виртуальном окружении, либо добавьте флаг --user или --break-system-packages (не рекомендуется):

```bash
pip3 install python-telegram-bot --user
# или
pip3 install python-telegram-bot --break-system-packages
```

### Настройка токена

1. Откройте файл `config.py`
2. Впишите ваш токен:
   ```python
   BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```

### Настройка камеры

1. Подключите USB-камеру к Raspberry Pi
2. Проверьте подключение:
   ```bash
   lsusb | grep -i camera
   ls /dev/video*
   ```
3. Протестируйте камеру:
   ```bash
   fswebcam -r 1280x720 --no-banner test_photo.jpg
   ```

### Запуск бота

```bash
python3 telegram_monitor_bot.py
```

### Подробная инструкция

Смотрите файл [`TELEGRAM_BOT_SETUP.md`](TELEGRAM_BOT_SETUP.md)

## 📊 Что проверяют скрипты

### telegram_monitor_bot.py
- **Telegram-бот**: мониторинг через мессенджер
- **Температура CPU**: текущая температура и предупреждения
- **Загрузка CPU**: средняя нагрузка за 1, 5, 15 минут
- **Память**: общая, используемая, доступная память
- **Диск**: использование файловой системы
- **Время работы**: uptime системы
- **Фото с камеры**: отправка фото через команду /photo
- **Безопасность**: ограничение доступа по ID пользователей

### system_test.py
- **Системная информация**: платформа, архитектура, процессор
- **Температура CPU**: текущая температура и предупреждения
- **Память**: общая, свободная, доступная память
- **Диск**: использование файловой системы
- **Сеть**: активные сетевые интерфейсы и IP адреса
- **Время работы**: uptime системы
- **GPIO**: доступность и работоспособность GPIO

## 🔧 Команды Telegram-бота

- `/start` - Запуск бота и показ приветствия
- `/status` - Показать статус системы
- `/photo` - Сделать и отправить фото с камеры
- `/help` - Подробная справка

## 🔧 Настройка прав доступа

Для корректной работы всех функций может потребоваться запуск с правами sudo:

```bash
sudo python3 system_test.py
```

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

## 🐛 Устранение проблем

### Ошибка "ModuleNotFoundError: No module named 'telegram'"
- Если используете apt: `sudo apt-get install python3-telegram-bot`
- Если используете pip: `pip3 install python-telegram-bot --user` или используйте виртуальное окружение

### Ошибка "fswebcam: command not found"
```bash
sudo apt-get install fswebcam
```

### Ошибка "No device found" при создании фото
1. Проверьте подключение камеры: `lsusb | grep -i camera`
2. Проверьте устройства: `ls /dev/video*`
3. Установите права: `sudo usermod -a -G video pi`
4. Перезагрузитесь: `sudo reboot`

### Ошибка доступа к системным файлам
```bash
sudo python3 system_test.py
```

### Ошибка кодировки
Убедитесь, что терминал поддерживает UTF-8:
```bash
export LANG=en_US.UTF-8
python3 system_test.py
```

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