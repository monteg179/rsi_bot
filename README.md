# rsi_bot
## ОПИСАНИЕ
Бот обрабатывает команды: add, remove, list
add – добавляет задание в планировщик
remove - удаляет задание из планировщика
list – просмотр заданий планировщика
Задания бывают: rsi, volatility, flats, trend

### задание rsi
параметры: `coin`, `timeframe`, `setpoint`
- `coin` – торговая пара
- `timeframe` – временной интервал: `30`, `240`
- `setpoint` – уставка
-
описание:
- получение свечей для заданных `coin` и `timeframe`
- вычисление `rsi`
- если `(rsi < setpoint * 0.15) или (rsi > setpoint * 0.85)`, отправляется сообщение со значением `rsi`
-
дополнительно:
- задание выполняться периодически с интервалом в `30` минут
- для вычисления `rsi` использовал `pandas_ta.rsi`
- 

### задание volatility
параметры: `coin`, `timeframe`, `setpoint`
- `coin` – торговая пара
- `timeframe` – временной интервал: `30`, `240`
- `setpoint` – уставка
-
описание:
- получение свечей для заданных `coin` и `timeframe`
- вычисление `atr`
- если `(atr < setpoint * 0.15) или (atr > setpoint * 0.85)`, отправляется сообщение со значением `atr`
-
дополнительно:
- задание выполняется периодически с интервалом в `30` минут
- для вычисления `atr` использовал `pandas_ta.atr`

### задание flats
параметры: `coin`, `timeframe`, `max_difference`, `min_length`, `va`
- `coin` – торговая пара
- `timeframe` – временной интервал, `30`, `60`, `240`, `1440`
- `max_difference` – диапазон цен закрытия флэта, в процентах
- `min_length` – минимальная длина флэта
- `va` – “размер” зоны стоимости, процент от общего объема сделок (`volume`)
-
описание:
- получение свечей для заданных `coin` и `timeframe`
- определяются флэты, для заданных параметров `max_difference` и `min_length`
- для каждого найденного флэта определятся `poc`, `val`, `vah`
- если флэты найдены, то отправляется сообщение с значениями `poc`, `val`, `vah` для всех найденных флэтов
-
дополнительно:
- задание выполняется периодически с интервалом в `30` минут.
-

### задание trend
параметры: `coin`, `timeframe`
- `coin` – торговая пара
- `timeframe` – временной интервал
-
описание:
- получение свечей для заданных `coin` и `timeframe`
- определение направления тренда для `[:-4]`
- анализ значений цены закрытия последних трех свечей, если выполняется условие для определения смены тренда, то отправляется сообщение («downtrend to uptrend» или «uptrend to downtrend»)
-
дополнительно:
- задание выполняется периодически с интервалом в `30` минут
- для определения направления тренда использовал `dmp` и `dmn` из `pandas_ta.adx`.

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
- `/add rsi <coin> <timeframe> <setpoint>` - добавить задание `rsi`
- `/add volatility <coin> <timeframe> <setpoint>` - добавить задание `volatility`
- `/add flats <coin> <timeframe> <max_difference> <min_length> <va>` - добавить задание `flats`
- `/add trend <coin> <timeframe>` - добавить задание `trend`

- `/remove rsi <coin> <timeframe> <setpoint>` - удалить задание `rsi`
- `/remove volatility <coin> <timeframe> <setpoint>` - удалить задание `volatility`
- `/remove flats <coin> <timeframe> <max_difference> <min_length> <va>` - удалить задание `flats`
- `/remove trend <coin> <timeframe>` - удалить задание `trend`

- `/list rsi` - просмотр заданий `rsi`
- `/list volatility` - просмотр заданий `volatility`
- `/list flats` - просмотр заданий `flats`
- `/list trend` - просмотр заданий `trens`
- `/list` - просмотр всех заданий


## ТЕХНОЛОГИИ
- Python 3.11
- Python-Telegram-Bot
- Pandas-TA

## АВТОРЫ
* Сергей Кузнецов - monteg179@yandex.ru



sudo docker image build -t monteg179/rsi_bot .
sudo docker container create --name rsi_bot --env-file /root/rsi_bot/.env  --restart always monteg179/rsi_bot
sudo docker container start rsi_bot


docker run -it --rm --env-file .env monteg179/rsi_bot /bin/bash