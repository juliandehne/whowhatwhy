#!/bin/bash

docker run --name postgres_local -it \
-v ~/nltk_data/twitter/postgres/data:/var/lib/postgresql/data \
-e PGDATA=/var/lib/postgresql/data \
-e POSTGRES_PASSWORD=postgres \
-e POSTGRES_USER=postgres \
-p 5432:5432 \
postgres
