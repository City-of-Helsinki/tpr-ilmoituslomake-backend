FROM python:3.7

RUN apt update
# https://docs.djangoproject.com/en/2.2/ref/contrib/gis/install/geolibs/
RUN apt-get install -y binutils libproj-dev gdal-bin

# add requirements.txt to the image
COPY requirements.txt /app/requirements.txt
WORKDIR /app/

# install python dependencies
RUN pip install -r requirements.txt

COPY ./ilmoituslomake/ /app
COPY ./local_dev/run_web.sh /app/run_web.sh
RUN chmod +x /app/run_web.sh