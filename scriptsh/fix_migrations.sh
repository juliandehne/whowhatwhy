sudo docker run -it --rm \
  --name fix_migrations \
  -v /opt/delab/whowhatwhy/logs/migrate:/code/logs \
  -v /opt/delab/whowhatwhy/database/migrations/delab:/code/delab/migrations \
  -v /opt/delab/whowhatwhy/database/migrations/blog:/code/blog/migrations \
  -v /opt/delab/whowhatwhy/database/migrations/users:/code/users/migrations \
  -v /opt/delab/whowhatwhy/database/migrations/mt_study:/code/mt_study/migrations \
  --env DJANGO_DATABASE=postgres \
  --env DJANGO_SUPERUSER_PASSWORD=delab \
  --env DJANGO_SUPERUSER_USERNAME=delab \
  --env DJANGO_SUPERUSER_EMAIL=julian.dehne@uni-goettingen.de \
  --network whowhatwhy_default \
  --link whowhatwhy_postgres_1 \
  delab-server \
  bash
