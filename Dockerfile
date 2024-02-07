FROM python:3.8-slim

EXPOSE 8000

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBIAN_FRONTEND noninteractive

# Install GCC and other build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip
RUN pip install gunicorn==20.1.0

COPY requirements.txt /
RUN pip install -r /requirements.txt

WORKDIR /app
COPY . /app

RUN ./manage.py collectstatic --noinput

