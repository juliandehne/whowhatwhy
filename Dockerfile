# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements-docker.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements-docker.txt
COPY requirements-ml-docker.txt /code/
RUN pip install -r requirements-ml-docker.txt
COPY . /code/
