docker-compose down
sudo rm -r pgdata
sudo mkdir pgdata
docker-compose build --no-cache tpr-ilmoituslomake
