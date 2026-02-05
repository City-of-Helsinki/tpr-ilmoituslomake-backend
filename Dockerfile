FROM python:3.10-bullseye

RUN apt update
# https://docs.djangoproject.com/en/2.2/ref/contrib/gis/install/geolibs/
RUN apt-get install -y binutils libproj-dev gdal-bin ca-certificates && \ 
    update-ca-certificates

# CGI DEV: remove comment from Zscaler certification related lines for development env
# requires 3 sertificate files (.crt, .pem, .der) in certificates/ under root
# This sertification configuration is tested on WSL ubuntu 22.04.5 LTS
# COPY certificates/ZscalerRootCertificate-2048-SHA256.crt /usr/local/share/ca-certificates/zscaler-root.crt
# COPY certificates/TeliaRootCAv2.crt /usr/local/share/ca-certificates/telia-root.crt
# RUN chmod 644 /usr/local/share/ca-certificates/*.crt && \
#    update-ca-certificates

# CGI DEV: remove comment from Zscaler certification related lines for development env
# requires 3 sertificate files (.crt, .pem, .der) in certificates/ under root
# This sertification configuration is tested on WSL ubuntu 22.04.5 LTS
# ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
# ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
# ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

# add requirements.txt to the image
COPY requirements.txt /app/requirements.txt
WORKDIR /app/

# install python dependencies
RUN pip install -r requirements.txt

# CGI DEV: remove comment from Zscaler certification related lines for development env
# requires 3 sertificate files (.crt, .pem, .der) in certificates/ under root
# This sertification configuration is tested on WSL ubuntu 22.04.5 LTS
# RUN cat /usr/local/share/ca-certificates/zscaler-root.crt >> /usr/local/lib/python3.10/site-packages/certifi/cacert.pem && \
#     cat /usr/local/share/ca-certificates/telia-root.crt >> /usr/local/lib/python3.10/site-packages/certifi/cacert.pem

COPY ./ilmoituslomake/ /app
COPY ./local_dev/run_web.sh /app/run_web.sh
RUN chmod +x /app/run_web.sh