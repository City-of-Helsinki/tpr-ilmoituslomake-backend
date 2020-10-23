CREATE USER ilmoituslomake;
ALTER USER ilmoituslomake WITH PASSWORD 'ilmoituslomake123';
CREATE DATABASE ilmoituslomake;
GRANT ALL PRIVILEGES ON DATABASE ilmoituslomake TO ilmoituslomake;
-- only in dev for extension creation
ALTER USER ilmoituslomake WITH SUPERUSER;