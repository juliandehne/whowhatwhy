FROM python:3.9.5

RUN apt-get -y update

# Install required packages
RUN apt-get -y install git

# Verify the installed versions
RUN python --version && \
    pip --version && \
    git --version


# installing the python libraries
ENV PYTHONUNBUFFERED=1
WORKDIR /code

RUN pip install -e git+https://github.com/juliandehne/delab-trees#egg=delab-trees
RUN pip install -e git+https://github.com/juliandehne/django-likert-field#egg=django-likert-field

COPY requirements-docker.txt /code/
COPY requirements_current.txt /code/

RUN pip install --upgrade pip
RUN pip install psycopg2-binary

RUN pip install -r requirements-docker.txt
RUN pip install -r requirements_current.txt

COPY . /code/

# RUN python /code/delab/sentiment/download_nltk.py

RUN export DJANGO_DATABASE=postgres
