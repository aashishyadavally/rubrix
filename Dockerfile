FROM python:3.8-slim-buster
USER root

WORKDIR /var/www/rubrix

RUN apt-get update && apt-get install nginx python3-pip linux-headers-amd64 build-essential gcc g++ python3-dev zip musl-dev unzip nano systemd -y

RUN python3 -m pip install numpy scipy tensorflow-hub tensorflow==2.5.0 scikit-image nltk spacy==3.1.0 flask matplotlib jupyter opencv-python kaggle scikit-learn

RUN python3 -m pip install uwsgi

COPY . .

RUN python3 -m pip install .

RUN apt-get install ffmpeg libsm6 libxext6  -y

COPY nlp /etc/nginx/sites-enabled/default
COPY entrypoint.sh /entrypoint.sh

EXPOSE 80
RUN chmod +x entrypoint.sh
RUN chmod 777 -R /root
RUN chmod 755 -R /var/www/rubrix
RUN chown -R www-data:www-data /var/www/rubrix
CMD  ["/entrypoint.sh"]