# Delab

Open Source Project to bundle political opinions in a concise and validated fashion and write a chatbot that acts as a
moderator. Uses natural language processing to sort out inflammatory or overly positive comments. It also deals with
other linguistic features in later stages.

Delab is the temporary repository for the delab project of Uni Göttingen.

# for programmers

Prerequisites:

- You need an academic account at Twitter in order to use the interactive features (Download Tweets and analyze them on
  the fly)
- Add a yaml file in /twitter/secret/keys_simple.yaml that contains the following fields

```yaml
  consumer_key:
  consumer_secret:
  bearer_token:
  access_token:
  access_token_secret: 
```

You can start the project with python3:

- install the required packages with pip (in requirements.txt)
- run "python manage.py makemigrations"
- run "python manage.py migrate"
- run "python manage.py runserver"
- run "python manage.py process_tasks -v 2 --log-std --duration -1 # this will allow the twitter download tasks to be
  started in the background

# Deploy with docker
sudo apt install docker docker-compose
docker build . -t delab-server
docker-compose down --volumes --remove-orphans
docker-compose up


# REST API

In order to get the conversations there are four endpoints

- <serverurl>/delab/rest/migration/tweets_json/
- <serverurl>/delab/rest/migration/tweets_excel/
- <serverurl>/delab/rest/migration/tweets_text/
- <serverurl>/delab/rest/migration/tweets_zip/

In order to get single conversations you need to specify id and (full|cropped), i.e.

- <serverurl>/delab/rest/migration/tweets_json/conversation/<conversation_id>/<(full|cropped)>

In order to get all conversation_ids that contain a valid cropped conversation tree use:

- <serverurl>/delab/rest/migration/tweets_text/conversation_ids
- Note: Firefox will round the last two decimals so use another tool to read the json response, i.e. curl, chrome,
  intellij 

In order to get all conversations bundled as a zip file you can use:

- <serverurl>/delab/rest/migration/tweets_zip/all/(both|cropped|full)