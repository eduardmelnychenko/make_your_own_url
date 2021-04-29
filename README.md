# rcmnd

# rebuild docker image
sudo docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
# remove volumes
sudo docker-compose down -v
# build image with compose (dev image)
# build image with compose (prod image)
sudo docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
# cleaning up
sudo docker-compose rm -f
# remove orphans
sudo docker rmi -f $(docker images -qf dangling=true)
# stop 
sudo docker stop rcmnd rcmnd-nginx redis-rcmnd
# restart docker image
sudo docker stop rcmnd && sudo docker start rcmnd
# list all running containers
sudo docker ps
# view logs
docker logs rcmnd

# connect to shell 
sudo docker exec -it <container name> /bin/bash

# localhost
http://localhost

# reload docker app
sudo touch wsgi.py

