echo "Run this as user tpr"
source ../venv/bin/activate
set -a; source ../.env; set+a;
gunicorn --bind=0.0.0.0:8008 ilmoituslomake.wsgi &
