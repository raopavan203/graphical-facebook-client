#!/bin/sh
#
# Script to install graphical-facebook-client server
#

sudo pip install flask
sudo apt-get install mongodb
sudo pip install mongoalchemy
sudo pip install flask-mongoalchemy
sudo apt-get install apache2
sudo apt-get install libapache2-mod-wsgi
sudo cp ./public_html/fb.wsgi /etc/apache2/sites-available
sudo echo "NameVirtualHost *:8081
Listen 8081" /etc/apache2/ports.conf
a2ensite fb
/etc/init.d/apache2 reload
