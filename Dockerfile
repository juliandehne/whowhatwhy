FROM ubuntu:focal
MAINTAINER fnndsc "dev@babymri.org"

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip

RUN apt-get install -y git

RUN apt install python-is-python3
RUN apt-mark hold python2 python2-minimal python2.7 python2.7-minimal libpython2-stdlib libpython2.7-minimal libpython2.7-stdlib

# Install dependencies and necessary tools
RUN apt-get install -y build-essential libssl-dev libffi-dev python3-dev wget

# Download Python 3.9 source code
RUN wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz

# Extract Python source code
RUN tar -xf Python-3.9.7.tgz

# Change into Python source code directory
WORKDIR /Python-3.9.7

# Configure the build
RUN ./configure --enable-optimizations

# Compile Python 3.9
RUN make -j $(nproc)

# Install Python 3.9
RUN make altinstall

# Cleanup
WORKDIR /
RUN rm -rf /Python-3.9.7*
RUN apt-get remove -y build-essential libssl-dev libffi-dev python3-dev wget
RUN apt-get autoremove -y

# Verify Python version
RUN python3.9 --version

# RUN apt install postgresql postgresql-contrib

ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements-docker.txt /code/
COPY requirements_current.txt /code/

RUN pip install --upgrade pip
RUN pip install psycopg2-binary
# RUN pip install torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install -r requirements-docker.txt
RUN pip install -r requirements_current.txt

RUN python -m nltk.downloader twitter_samples
RUN python -m nltk.downloader stopwords
RUN python -m nltk.downloader vader_lexicon

RUN pip install -e git+https://github.com/juliandehne/delab-trees#egg=delab-trees
#RUN pip install --upgrade "jax[cpu]"
COPY . /code/

# RUN python /code/delab/sentiment/download_nltk.py

RUN export DJANGO_DATABASE=postgres

