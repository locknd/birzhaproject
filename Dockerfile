FROM python:3.11-slim

WORKDIR /app

# если есть requirements.txt — скопировать и установить зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# потом копируем всё приложение
COPY . .

EXPOSE 8000

# по умолчанию запускаем uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]