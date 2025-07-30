# Настройка Telegram-бота для мониторинга Raspberry Pi

## 📋 Пошаговая инструкция

### 1. Создание Telegram-бота

1. **Откройте Telegram** и найдите @BotFather
2. **Отправьте команду** `/newbot`
3. **Введите имя бота** (например, "Raspberry Pi Monitor")
4. **Введите username** (например, "my_pi_monitor_bot") - должен заканчиваться на "bot"
5. **Скопируйте токен** - он выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

### 2. Установка зависимостей

```bash
# Обновляем систему
sudo apt-get update

# Устанавливаем Python и pip (если не установлены)
sudo apt-get install python3 python3-pip

# Устанавливаем библиотеку для Telegram
pip3 install python-telegram-bot

# Или через apt (альтернативный способ)
sudo apt-get install python3-telegram-bot
```

### 3. Настройка бота

1. **Откройте файл** `telegram_monitor_bot.py`
2. **Замените строку** `TELEGRAM_TOKEN = "YOUR_BOT_TOKEN_HERE"` на ваш токен:
   ```python
   TELEGRAM_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```

### 4. Настройка безопасности (опционально)

Для ограничения доступа только определенным пользователям:

1. **Получите ваш ID** в Telegram:
   - Напишите боту @userinfobot
   - Он покажет ваш ID (например, 123456789)

2. **Добавьте ID в список разрешенных**:
   ```python
   ALLOWED_USERS = [123456789]  # Ваш ID
   ```

### 5. Запуск бота

```bash
# Запуск в обычном режиме
python3 telegram_monitor_bot.py

# Запуск в фоне (рекомендуется)
nohup python3 telegram_monitor_bot.py > bot.log 2>&1 &

# Проверка работы
tail -f bot.log
```

### 6. Тестирование

1. **Найдите вашего бота** в Telegram по username
2. **Отправьте команду** `/start`
3. **Проверьте команду** `/status`

## 🔧 Команды бота

- `/start` - Запуск бота и показ приветствия
- `/status` - Показать статус системы (температура, CPU, память, диск)
- `/help` - Показать справку

## 📊 Что показывает /status

- **🌡️ Температура CPU** - текущая температура с оценкой состояния
- **⚡ Загрузка CPU** - средняя нагрузка за 1, 5 и 15 минут
- **🧠 Память** - общая, используемая и доступная память
- **💾 Диск** - использование файловой системы
- **⏰ Время работы** - сколько система работает без перезагрузки

## 🚨 Статусы системы

- **✅** - Нормальное состояние
- **⚠** - Повышенные показатели (внимание)
- **❌** - Критические показатели (требует действий)

## 🔄 Автозапуск при загрузке

### Способ 1: systemd сервис

1. **Создайте файл сервиса**:
```bash
sudo nano /etc/systemd/system/pi-monitor-bot.service
```

2. **Добавьте содержимое**:
```ini
[Unit]
Description=Raspberry Pi Monitor Telegram Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/raspberry_scripts
ExecStart=/usr/bin/python3 /home/pi/raspberry_scripts/telegram_monitor_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. **Активируйте сервис**:
```bash
sudo systemctl daemon-reload
sudo systemctl enable pi-monitor-bot
sudo systemctl start pi-monitor-bot
```

4. **Проверьте статус**:
```bash
sudo systemctl status pi-monitor-bot
```

### Способ 2: crontab

```bash
# Откройте crontab
crontab -e

# Добавьте строку для автозапуска при загрузке
@reboot cd /home/pi/raspberry_scripts && python3 telegram_monitor_bot.py > bot.log 2>&1 &
```

## 🐛 Устранение проблем

### Ошибка "ModuleNotFoundError: No module named 'telegram'"
```bash
pip3 install python-telegram-bot --upgrade
```

### Ошибка "Permission denied"
```bash
# Проверьте права на файл
chmod +x telegram_monitor_bot.py

# Или запустите с sudo (не рекомендуется)
sudo python3 telegram_monitor_bot.py
```

### Бот не отвечает
1. Проверьте правильность токена
2. Убедитесь, что интернет работает
3. Проверьте логи: `tail -f bot.log`

### Ошибка кодировки
```bash
export LANG=en_US.UTF-8
python3 telegram_monitor_bot.py
```

## 📈 Расширение функциональности

### Добавление отправки фото с камеры

1. **Установите библиотеку для работы с камерой**:
```bash
sudo apt-get install python3-picamera
pip3 install opencv-python
```

2. **Добавьте функцию в бота**:
```python
async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка фото с камеры"""
    try:
        # Создаем фото
        camera = cv2.VideoCapture(0)
        ret, frame = camera.read()
        if ret:
            cv2.imwrite('temp_photo.jpg', frame)
            camera.release()
            
            # Отправляем фото
            with open('temp_photo.jpg', 'rb') as photo:
                await update.message.reply_photo(photo)
            
            # Удаляем временный файл
            os.remove('temp_photo.jpg')
        else:
            await update.message.reply_text("❌ Не удалось получить фото с камеры")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
```

3. **Добавьте обработчик**:
```python
application.add_handler(CommandHandler("photo", photo))
```

## 🔒 Безопасность

- **Не публикуйте токен** в открытых репозиториях
- **Используйте список разрешенных пользователей** для ограничения доступа
- **Регулярно обновляйте** библиотеки
- **Мониторьте логи** на подозрительную активность

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `tail -f bot.log`
2. Убедитесь, что все зависимости установлены
3. Проверьте подключение к интернету
4. Перезапустите бота: `sudo systemctl restart pi-monitor-bot` 