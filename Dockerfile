FROM python:3.11

WORKDIR /app

COPY rsi_bot rsi_bot

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt --no-cache-dir

CMD ["python", "-m", "rsi_bot.main"]