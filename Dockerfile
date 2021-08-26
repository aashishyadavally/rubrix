FROM python:3.8-slim-buster
USER root

# where the project lives
WORKDIR /var/www/rubrix

# install system requirements
RUN apt-get update && apt-get install\
    nginx\
    python3-pip\
    linux-headers-amd64\
    build-essential\
    gcc\
    g++\
    python3-dev\
    zip\
    unzip\
    musl-dev\
    nano\
    ffmpeg\
    libsm6\
    libxext6\
    systemd -y

# install pip requirements (note that uwsgi is required regardless of what else you may modify)
RUN python3 -m pip install\
    numpy\
    scipy\
    tensorflow-hub\
    tensorflow==2.5.0\
    scikit-image\
    nltk\
    spacy==3.1.0\
    flask\
    matplotlib\
    jupyter\
    opencv-python\
    kaggle\
    scikit-learn\
    uwsgi

# install the models spacy needs
RUN python3 -m spacy download en_core_web_sm
RUN python3 -m spacy download en_core_web_md
RUN python3 -m spacy download en_core_web_lg

# copy project to WORKDIR
COPY . .

# install rubrix
RUN python3 -m pip install .

# install darknet
RUN cd /var/www/rubrix/rubrix/index && bash quick_setup.sh

# setup internal reverse proxy and entrypoint
COPY nlp /etc/nginx/sites-enabled/default
COPY entrypoint.sh /entrypoint.sh

# expose external port 80 for nginx to proxy through
EXPOSE 80

# fix some permissions
RUN chmod +x entrypoint.sh
RUN chmod 777 -R /root
RUN chmod 755 -R /var/www/rubrix
RUN chown -R www-data:www-data /var/www/rubrix

# what gets ran when the docker container is launched
CMD  ["/entrypoint.sh"]