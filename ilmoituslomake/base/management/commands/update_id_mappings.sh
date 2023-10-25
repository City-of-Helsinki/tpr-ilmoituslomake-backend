cd /opt/tpr-ilmoituslomake-backend/
source /opt/tpr-ilmoituslomake-backend/venv/bin/activate
set -a; source /opt/tpr-ilmoituslomake-backend/.env; set +a;
cd /opt/tpr-ilmoituslomake-backend/ilmoituslomake/
python manage.py import_id_mappings > /opt/tpr-ilmoituslomake-backend/id_mappings_output.log
python manage.py export_id_mappings >> /opt/tpr-ilmoituslomake-backend/id_mappings_output.log
deactivate
