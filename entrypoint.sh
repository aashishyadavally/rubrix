#!/bin/bash
service nginx start
cd /var/www/rubrix/rubrix/web
uwsgi --ini uwsgi.ini --lazy-apps