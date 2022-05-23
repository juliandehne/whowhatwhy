# Delab

Open Source Project to bundle political opinions in a concise and validated fashion and write a chatbot that acts as a
moderator. Uses natural language processing to sort out inflammatory or overly positive comments. It also deals with
other linguistic features in later stages.

Delab is the temporary repository for the delab project of Uni Göttingen.

# What makes this project different

Normally, django is used as a tool to create a business website. Here, it is interlaced with the bot development and the precursory 
man-in-the-loop experiments!

# Getting started

## Mission statement

This code base is meant as an integrative framework that will serve several functions

- It is a prototyp of the delab bot, that will interact with users in social media trying to encourage pluralistic and
  productive discussions
- It is a utility to access data downloaded from social media platforms within the delab project and provide interfaces
  for our partners
- It is a testing ground for man in the loop experiments with social media data and artificial intelligence

## Assumed Knowledge

The code is not going to make sense if you don't have a basic background in

- python programming
- sql databases
- the django framework
- jupyter notebooks

In general the framework is very lightweight.

## Basic Setup and Requirements

In order to use the full range of the utility, access to google perspective api, twitter academic account and the reddit
api is assumed. The consumer key etc. references Twitter. In order to get the project ready there are these steps:

1. Add a yaml file in twitter/secret/keys_simple.yaml that contains the following fields

```yaml
  consumer_key:
  consumer_secret:
  bearer_token:
  access_token:
  access_token_secret:
  reddit_secret:
  reddit_script_id:
  gcloud_delab: 
```

2. You need a 64 bit python and enough memory availble (at least 4k) in order to run the analytics
3. Install the required packages with pip (in requirements.txt)
4. Install a PostGres DB either with docker or as a native service.
    1. it should listen at the stadard port
    2. there should be a database with name "delab" that can be accessed by user "delab" with password "delab"
    3. As an alternative to the last two points, use the start_postgres_docker.sh in the folder called "scriptsh"

## Entry points for using the code actively

1. Run the Code as a Django Website for Man-In-the-Loop experiments
2. Run Django Scripts (Python Scripts that connect to the Django models) sharing the DB from 1
3. Run JupyterNotebooks that connects to the DB from 1
4. Provide data downloaded to project partners

### Running the Project as a Website

After having completet the basic setup (especially the yaml file with the api keys), you are ready to proceed to fire up
the website for the interactive experiments. For this you need to complete the following steps in the project directory:

1. run "python manage.py makemigrations"
2. run "python manage.py migrate"
3. run "python manage.py runserver 0.0.0.0:8000"
4. run "python manage.py process_tasks -v 2 --log-std --duration -1 # this will allow the twitter download tasks to be
   started in the background

```bash
bash scriptsh/start_postgres_docker.sh
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
python manage.py process_tasks -v 2 --log-std --duration -1
```

The first two steps will crate the schema in the database. The third starts the server. The fourth one starts the
background demon that is needed for long-running tasks like downloading twitter data.

### Using Django Scripts

Many parts of the pipeline can be started directly with django scripts. These differ from regular scripts in the sense
that you can use django functionality that accesses the database. The following is a short overview over the important
scripts

1. download_conversations: this will download Twitter conversations as a structured tree and store them in the db
2. download_terrible_tweets: using a dictionary approach this will download extremely intolerant tweets
3. pipeline: this will run a series of analytics on the downloaded conversations including sentiment analysis and topic
   modelling and will fill the candidate table for labeing tweets as possibly be a moderator or not
4. download_author_tweets: download additional data on the authors, i.e. their timeline
5. download_author_names: this will download all the data available in the author's user profile

NOTE: Django scripts need to be run differently then regular python scripts. The command is:

```bash
python manage.py runscript scriptname_without_file_ending [--script-args arg1 arg2] 
```

### Using Jupyter Notebooks

In the folder notebooks you can access the notebooks by using your own jupyter notebook server

### Provide Data to Project Partners

There are several options to get data for analysis without having having to code yourselves:

- use the download tab on the website 
- use the rest-services programatically. For this see the [wiki entry](https://github.com/juliandehne/delab/wiki/REST-Services).

# Code Overview

- django_project contains the settings.py file which shows most decisions
- delab/templates contains the different webpages
- delab/models.py contains the tables and main concepts
- delab/views.py contains the view-controllers
- delab/tasks.py contains the background tasks that are triggered by the website when downloading data
- delab/signals.py contains some anti-patterns that after a models is saved additional events are triggered
- delab/corpus contains the logic for downloading conversations in social media, espc. twitter
- delab/nce contains the important logic for the basic prototype that answers intolerant tweets

# Deploy with docker

```shell
sudo apt install docker docker-compose
docker build . -t delab-server
docker-compose down --volumes --remove-orphans
docker-compose up
```

# Ongoing studies and the corresponding setup

## Moderation Mining 

The idea here is to find tweets that try to moderate the ongoing chat based. 
For a closer look, go to the [wiki page](https://github.com/juliandehne/delab/wiki/moderation_mining)

## Norm Culture Experiment

The idea here is to experiment with different strategies to approach norm violations like intolerance.
For a closer look, go to the [wiki page](https://github.com/juliandehne/delab/wiki/nce)

