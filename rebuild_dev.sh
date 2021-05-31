docker-compose down
sudo rm -r pgdata
sudo mkdir pgdata
sudo rm -r ./ilmoituslomake/base/migrations
sudo rm -r ./ilmoituslomake/users/migrations
sudo rm -r ./ilmoituslomake/moderation/migrations
sudo rm -r ./ilmoituslomake/notification_form/migrations
docker-compose build tpr-ilmoituslomake
