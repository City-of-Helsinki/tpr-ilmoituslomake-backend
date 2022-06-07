echo "Run this as user tpr"
source ../venv/bin/activate
set -a; source ../.env; set +a;
# cd ilmoituslomake && python manage.py runserver 0.0.0.0:8008 &
gunicorn --bind=0.0.0.0:8008 ilmoituslomake.wsgi &
