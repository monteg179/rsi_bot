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
- `/add rsi <coin> <timeframe> <setpoint>` - добавить задание RSI
- `/add atr <coin> <timeframe> <setpoint>` - добавить задание ATR
- `/add poc <coin> <timeframe> <max_difference> <min_length> <va>` - добавить задание POC
- `/remove rsi <coin> <timeframe> <setpoint>` - удалить задание RSI 
- `/remove atr <coin> <timeframe> <setpoint>` - удалить задание ATR
- `/remove poc <coin> <timeframe> <max_difference> <min_length> <va>` - удалить задание POC
- `/list rsi` - просмотр заданий RSI
- `/list atr` - просмотр заданий ATR
- `/list poc` - просмотр заданий POC
- `/list` - просмотр всех заданий


## ТЕХНОЛОГИИ
- Python 3.11
- Python-Telegram-Bot
- Pandas-TA

## АВТОРЫ
* Сергей Кузнецов - monteg179@yandex.ru
