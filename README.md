# Community Archive

## Deployment

Install prerequisites:

    $ sudo apt install python3-dev default-libmysqlclient-dev build-essential \
      poppler utils

Install web and db server:

    $ sudo apt install apache2 libapache2-mod-wsgi-py3 mariadb-server

Create virtual env and install python dependencies:

    $ python3 -m venv venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt
    $ pip install mysqlclient

Create database:
    
    $ sudo mysql
    $ CREATE DATABASE community_archive CHARACTER SET utf8;
    $ CREATE USER 'community_archive'@'localhost' IDENTIFIED BY [PASSWORD];
    $ GRANT ALL PRIVILEGES ON community_archive.* TO 'community_archive'@'localhost';
    $ FLUSH PRIVILEGES;
    $ EXIT;

Create static and media directories:

    $ sudo mkdir -p /var/www/community_archive/{media,static}
    $ sudo chown -R $USER:www-data /var/www/community_archive/static
    $ sudo chown -R www-data:www-data /var/www/community_archive/media

Configure app:

    $ cp env.sample .env

Customize the configuration to your environment.

Check if deployment settings are ok:

    $ python3 manage.py check --deploy

Copy static files:

    $ python3 manage.py collectstatic

Migrate database:

    $ python3 manage.py migrate

Configure Apache (customize configuration to your needs):

    $ sudo cp apache.conf /etc/apache2/sites-available/community_archive.conf
    $ sudo a2ensite community_archive.conf
    $ sudo a2dissite 000-default.conf
    $ sudo systemctl reload apache2

Configure SSL for WACZ viewing to work (not covered here)

Install redis:

    $ sudo apt install redis-server

Configure celery systemd service:

    $ sudo cp celery.service /etc/systemd/system/community-archive-celery.service
    $ sudo systemctl daemon-reload
    $ sudo systemctl enable community-archive-celery.service
    $ sudo systemctl start community-archive-celery.service

Create superuser:

    $ python3 manage.py createsuperuser