FROM python:3.8-slim

WORKDIR /app

COPY ./requirements.txt ./requirements.txt

COPY . /app/

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

RUN rm requirements.txt