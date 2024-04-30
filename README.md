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
бот поддерживает команды:
- `/add rsi <coin> <timeframe> <setpoint>` - добавить задание RSI
- `/add volatility <coin> <timeframe> <setpoint>` - добавить задание ATR
- `/add flats <coin> <timeframe> <max_difference> <min_length> <va>` - добавить задание POC
- `/add trend <coin> <timeframe>` - добавить задание TREND

- `/remove rsi <coin> <timeframe> <setpoint>` - удалить задание RSI 
- `/remove volatility <coin> <timeframe> <setpoint>` - удалить задание ATR
- `/remove flats <coin> <timeframe> <max_difference> <min_length> <va>` - удалить задание POC
- `/remove trend <coin> <timeframe>` - удалить задание TREND

- `/list rsi` - просмотр заданий RSI
- `/list volatility` - просмотр заданий ATR
- `/list flats` - просмотр заданий POC
- `/list trend` - просмотр заданий TREND
- `/list` - просмотр всех заданий


## ТЕХНОЛОГИИ
- Python 3.11
- Python-Telegram-Bot
- Pandas-TA

## АВТОРЫ
* Сергей Кузнецов - monteg179@yandex.ru
