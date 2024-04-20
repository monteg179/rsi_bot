# rsi_bot
## ЗАПУСК
1. клонировать репозиторий:
```sh
git clone -b 'develop' https://github.com/monteg179/rsi_bot.git
cd rsi_bot
```
2. создать файл .env с таким содержанием
```
TELEGRAM_TOKEN=<token>
```
3. создать и активировать виртуальное окружение
```sh
poetry install
poetry shell
```
или так
```sh
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
4. запутить бота
```sh
poetry run bot
```
или так 
```sh
python rsi_bot/main.py
```

## ИСПОЛЬЗОВАНИЕ
Бот поддерживает команды:
- /rsi <coin> <timeframe> <min> <max>
- /atr <coin> <timeframe> <min> <max>
- /poc 
- /trend
- /stop


## ТЕХНОЛОГИИ
- Python 3.11
- Python-Telegram-Bot
- Pandas-TA

## АВТОРЫ
* Сергей Кузнецов - monteg179@yandex.ru
