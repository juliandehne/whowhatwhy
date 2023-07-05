FROM ubuntu:20.04
RUN apt-get update && apt-get install -y python3.9 python3.9-dev

# RUN apt install postgresql postgresql-contrib

ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements-docker.txt /code/
COPY requirements_current.txt /code/

RUN pip install --upgrade pip
RUN pip install psycopg2-binary
# RUN pip install torch==1.6.0+cpu torchvision==0.7.0+cpu -f https://download.pytorch.org/whl/torch_stable.html
RUN --mount=type=cache,mode=0755,target=/root/.cache pip install -r
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

