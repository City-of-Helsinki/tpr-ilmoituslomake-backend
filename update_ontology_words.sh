cd /opt/tpr-ilmoituslomake-backend/
source ./venv/bin/activate
set -a; source .env; set +a;
cd /opt/tpr-ilmoituslomake-backend/ilmoituslomake/
python manage.py import_ontology_words
deactivate
