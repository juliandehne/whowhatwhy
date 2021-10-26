sudo docker-compose down
git pull
sudo docker build . -t delab-server
nohup sudo docker-compose up &> /dev/null &
# nohup sudo docker-compose up run_server process_tasks &> /dev/null &

