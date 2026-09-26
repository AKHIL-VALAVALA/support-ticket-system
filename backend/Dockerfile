FROM python:3.12-slim
WORKDIR /app
RUN apt-get update && apt-get install -y default-libmysqlclient-dev pkg-config gcc && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ .
ENV DJANGO_DEBUG=False
EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn ticketsystem.wsgi:application --bind 0.0.0.0:${PORT:-8000}"]
