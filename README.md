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


описание:
- получение свечей для заданных `coin` и `timeframe`
- вычисление `rsi`
- если `(rsi < setpoint * 0.15) или (rsi > setpoint * 0.85)`, отправляется сообщение со значением `rsi`


дополнительно:
- задание выполняться периодически с интервалом в `30` минут
- для вычисления `rsi` использовал `pandas_ta.rsi`
 

### задание volatility
параметры: `coin`, `timeframe`, `setpoint`
- `coin` – торговая пара
- `timeframe` – временной интервал: `30`, `240`
- `setpoint` – уставка


описание:
- получение свечей для заданных `coin` и `timeframe`
- вычисление `atr`
- если `(atr < setpoint * 0.15) или (atr > setpoint * 0.85)`, отправляется сообщение со значением `atr`


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


описание:
- получение свечей для заданных `coin` и `timeframe`
- определяются флэты, для заданных параметров `max_difference` и `min_length`
- для каждого найденного флэта определятся `poc`, `val`, `vah`
- если флэты найдены, то отправляется сообщение с значениями `poc`, `val`, `vah` для всех найденных флэтов
-
дополнительно:
- задание выполняется периодически с интервалом в `30` минут.


### задание trend
параметры: `coin`, `timeframe`
- `coin` – торговая пара
- `timeframe` – временной интервал


описание:
- получение свечей для заданных `coin` и `timeframe`
- определение направления тренда для `[:-4]`
- анализ значений цены закрытия последних трех свечей, если выполняется условие для определения смены тренда, то отправляется сообщение («downtrend to uptrend» или «uptrend to downtrend»)


дополнительно:
- задание выполняется периодически с интервалом в `30` минут
- для определения направления тренда использовал `dmp` и `dmn` из `pandas_ta.adx`.

## ЗАПУСК
1. клонировать репозиторий:
```sh
git clone -b 'develop' https://github.com/monteg179/rsi_bot.git
cd rsi_bot
```
2. создать файл `.env` с таким содержанием
```
TELEGRAM_TOKEN=<token>
```
3. создать, активировать виртуальное окружение, и запустить бота
```sh
poetry install
poetry shell
poetry run bot
```

## ИСПОЛЬЗОВАНИЕ
бот поддерживает команды:
- `/add rsi <coin> <timeframe> <setpoint>` - добавить задание `rsi`<br>Например: `/add rsi BTCUSD 30 0.0`
- `/add volatility <coin> <timeframe> <setpoint>` - добавить задание `volatility`<br>Например: `/add volatility BTCUSD 30 0.0`
- `/add flats <coin> <timeframe> <max_difference> <min_length> <va>` - добавить задание `flats`<br>Например: `/add flats BTCUSD 30 1.0 10 68.0`
- `/add trend <coin> <timeframe>` - добавить задание `trend`<br>Например: `/add trend BTCUSD 1440`
- `/remove rsi <coin> <timeframe> <setpoint>` - удалить задание `rsi`<br>Например: `/remove rsi BTCUSD 30 0.0`
- `/remove volatility <coin> <timeframe> <setpoint>` - удалить задание `volatility`<br>Например: `/remove volatility BTCUSD 30 0.0`
- `/remove flats <coin> <timeframe> <max_difference> <min_length> <va>` - удалить задание `flats`<br>Например: `/remove flats BTCUSD 30 1.0 10 68.0`
- `/remove trend <coin> <timeframe>` - удалить задание `trend`<br>Например: `/remove trend BTCUSD 1440`
- `/list rsi` - просмотр заданий `rsi`
- `/list volatility` - просмотр заданий `volatility`
- `/list flats` - просмотр заданий `flats`
- `/list trend` - просмотр заданий `trens`
- `/list` - просмотр всех заданий


## ТЕХНОЛОГИИ
- Python 3.11
- Poetry
- Pyenv
- Python-Telegram-Bot
- Pandas-TA
- Docker
- Github Actions

## АВТОРЫ
* Сергей Кузнецов - monteg179@yandex.ru
