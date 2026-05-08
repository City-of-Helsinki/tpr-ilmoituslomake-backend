docker-compose down
sudo rm -r pgdata
sudo mkdir pgdata
docker-compose build tpr-ilmoituslomake-db tpr-ilmoituslomake
