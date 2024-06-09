FROM python:3.11

# COPY rsi_bot rsi_bot
# COPY requirements.txt .
WORKDIR /app
COPY . backend
RUN pip install --upgrade pip
RUN pip install -r backend/requirements.txt --no-cache-dir
CMD ["python", "-m", "backend.main"]