FROM python:3.7-slim

WORKDIR /srv/app

COPY requirements.txt /srv/app

RUN apt-get update && \
    apt-get install -y \
        build-essential \
        make \
        gcc \
        pkg-config
        
#ython3-matplotlib


RUN pip install --upgrade pip -r requirements.txt

COPY app/. /srv/app/app
COPY run.py /srv/app
COPY config.py /srv/app
COPY messages.pot /srv/app

RUN mkdir logs
