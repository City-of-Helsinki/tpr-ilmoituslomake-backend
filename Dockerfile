FROM python:3.7

RUN apt update

# create user
RUN groupadd ilmoituslomake --gid 501
RUN adduser --disabled-password --gecos '' --system --shell /bin/bash --uid 501 ilmoituslomake
RUN usermod -a -G ilmoituslomake ilmoituslomake
RUN echo "ilmoituslomake   ALL = NOPASSWD: ALL" >> /etc/sudoers

# add requirements.txt to the image
COPY --chown=ilmoituslomake:users requirements.txt /app/requirements.txt
WORKDIR /app/

# install python dependencies
RUN pip install -r requirements.txt

COPY --chown=ilmoituslomake:users ./ilmoituslomake/ /app
COPY --chown=ilmoituslomake:users ./local_dev/run_web.sh /app/run_web.sh
RUN chmod +x /app/run_web.sh