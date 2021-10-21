FROM ubuntu:latest
MAINTAINER fnndsc "dev@babymri.org"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt install python-is-python3
RUN apt-mark hold python2 python2-minimal python2.7 python2.7-minimal libpython2-stdlib libpython2.7-minimal libpython2.7-stdlib

# RUN apt install postgresql postgresql-contrib

ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements-docker.txt /code/

RUN pip install --upgrade pip
RUN pip install psycopg2-binary
RUN pip install torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install -r requirements-docker.txt

RUN pip install trax==1.3.9
RUN pip uninstall jax
RUN pip install --upgrade "jax[cpu]"

COPY . /code/

RUN python /code/delab/sentiment/download_nltk.py

RUN export DJANGO_DATABASE=postgres

