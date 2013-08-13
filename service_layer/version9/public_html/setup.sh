#!/bin/sh
#
# Script to install graphical-facebook-client server
#

curr_dir=`pwd`
dir=`dirname $0`
FILE_PATH=`cd  $dir;pwd`
echo "Path to this file : $FILE_PATH"
sed -i -e 's@install-path@'$FILE_PATH'@g' ${FILE_PATH}/wsgi/fb.wsgi
sed -i -e 's@install-path@'$FILE_PATH'@g' ${FILE_PATH}/fb
echo 'INSTALL PIP'
sudo apt-get install python-pip
echo 'INSTALL FLASK'
sudo pip install flask
echo 'INSTALL APACHE2'
sudo apt-get install apache2
echo 'INSTALL MOD-WSGI'
sudo apt-get install libapache2-mod-wsgi
echo 'INSTALL MONGODB'
sudo apt-get install mongodb
echo 'INSTALL MONGOALCHEMY'
sudo pip install mongoalchemy
echo 'INSTALL FLASK-MONGOALCHEMY'
sudo pip install flask-mongoalchemy
mongo < init_mongo.js
sudo cp ${FILE_PATH}/fb /etc/apache2/sites-available
sudo bash -c "echo -e NameVirtualHost *:8081 >> /etc/apache2/ports.conf"
sudo bash -c "echo -e Listen 8081 >> /etc/apache2/ports.conf"
sudo a2ensite fb
sudo /etc/init.d/apache2 reload

