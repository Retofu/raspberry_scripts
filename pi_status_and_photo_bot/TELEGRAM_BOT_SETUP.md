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

# Устанавливаем библиотеку для Telegram (рекомендуемый способ)
sudo apt-get install python3-telegram-bot

# Устанавливаем fswebcam для работы с камерой
sudo apt-get install fswebcam
```

**Если нужен pip (например, для виртуального окружения):**

```bash
# Виртуальное окружение (рекомендуется для pip)
sudo apt-get install python3-venv
python3 -m venv ~/telegram_bot_env
source ~/telegram_bot_env/bin/activate
pip install python-telegram-bot

# Запуск бота из виртуального окружения:
python telegram_monitor_bot.py
```

**Если pip3 install не работает из-за ошибки externally-managed-environment:**
- Используйте только в виртуальном окружении, либо добавьте флаг --user или --break-system-packages (не рекомендуется):

```bash
pip3 install python-telegram-bot --user
# или
pip3 install python-telegram-bot --break-system-packages
```

### 3. Настройка бота

1. **Откройте файл** `config.py`
2. **Замените строку** `BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"` на ваш токен:
   ```python
   BOT_TOKEN = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
   ```

**Примечание:** Токен теперь хранится в отдельном файле `config.py` для безопасности.

### 4. Настройка камеры

1. **Подключите USB-камеру** к Raspberry Pi
2. **Проверьте, что камера определилась**:
   ```bash
   lsusb | grep -i camera
   ```
3. **Проверьте доступные устройства**:
   ```bash
   ls /dev/video*
   ```
4. **Протестируйте fswebcam**:
   ```bash
   fswebcam -r 1280x720 --no-banner test_photo.jpg
   ```

### 5. Настройка безопасности (опционально)

Для ограничения доступа только определенным пользователям:

1. **Получите ваш ID** в Telegram:
   - Напишите боту @userinfobot
   - Он покажет ваш ID (например, 123456789)

2. **Добавьте ID в список разрешенных** в файле `telegram_monitor_bot.py`:
   ```python
   ALLOWED_USERS = [123456789]  # Ваш ID
   ```

### 6. Запуск бота

```bash
# Запуск в обычном режиме
python3 telegram_monitor_bot.py

# Запуск в фоне (рекомендуется)
nohup python3 telegram_monitor_bot.py > bot.log 2>&1 &

# Проверка работы
tail -f bot.log
```

### 7. Тестирование

1. **Найдите вашего бота** в Telegram по username
2. **Отправьте команду** `/start`
3. **Проверьте команду** `/status`
4. **Проверьте команду** `/photo`

## 🔧 Команды бота

- `/start` - Запуск бота и показ приветствия
- `/status` - Показать статус системы (температура, CPU, память, диск)
- `/photo` - Сделать и отправить фото с камеры
- `/help` - Показать подробную справку

## 📊 Что показывает /status

- **🌡️ Температура CPU** - текущая температура с оценкой состояния
- **⚡ Загрузка CPU** - средняя нагрузка за 1, 5 и 15 минут
- **🧠 Память** - общая, используемая и доступная память
- **💾 Диск** - использование файловой системы
- **⏰ Время работы** - сколько система работает без перезагрузки

## 📸 Что делает /photo

- **Делает фото** с USB-камеры через fswebcam
- **Разрешение**: 1280x720 пикселей
- **Качество**: 85% JPEG
- **Стабилизация**: пропускает 3 кадра перед съемкой
- **Баннер**: убирает дату/время с фото
- **Автоочистка**: удаляет временные файлы после отправки

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
- Если используете apt: `sudo apt-get install python3-telegram-bot`
- Если используете pip: `pip3 install python-telegram-bot --user` или используйте виртуальное окружение

### Ошибка "Permission denied"
```bash
# Проверьте права на файл
chmod +x telegram_monitor_bot.py

# Или запустите с sudo (не рекомендуется)
sudo python3 telegram_monitor_bot.py
```

### Ошибка "fswebcam: command not found"
```bash
sudo apt-get install fswebcam
```

### Ошибка "No device found" при создании фото
1. Проверьте подключение камеры: `lsusb | grep -i camera`
2. Проверьте устройства: `ls /dev/video*`
3. Установите права: `sudo usermod -a -G video pi`
4. Перезагрузитесь: `sudo reboot`

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

### Настройка параметров фото

В функции `take_photo()` можно изменить параметры:

```python
# Разрешение
-r 1920x1080  # Full HD
-r 640x480    # VGA

# Качество JPEG
--jpeg 95     # Высокое качество
--jpeg 70     # Низкое качество

# Количество кадров для стабилизации
-S 5          # Больше кадров = лучше стабилизация

# Добавить баннер с датой/временем
# Уберите --no-banner для добавления баннера
```

## 📞 Поддержка

При возникновении проблем:
1. Проверьте логи: `tail -f bot.log`
2. Убедитесь, что все зависимости установлены
3. Проверьте подключение к интернету
4. Проверьте работу камеры: `fswebcam test.jpg`
5. Перезапустите бота: `sudo systemctl restart pi-monitor-bot`