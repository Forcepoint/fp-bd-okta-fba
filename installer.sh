#!/bin/bash

#install python3
echo "Installing python3"
sudo yum install -y https://centos7.iuscommunity.org/ius-release.rpm
#sudo yum groups install "Development Tools" -y
#sudo yum update -y
sudo yum install -y python36u python36u-libs python36u-devel python36u-pip

# install python modules
sudo pip3 install flask
sudo pip3 install requests
sudo pip3 install confluent-kafka
# check if config file is exists
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
CONFIG_FILE=$DIR/configs.json

if [ ! -f "$CONFIG_FILE" ]; then
    echo "The config file:$CONFIG_FILE does not exist"
    exit 1
fi

# create required directories
APPLICATION_DIRECTORY="$(python3 $DIR/installer_helper.py $CONFIG_FILE)"
echo "**** Moving the application files to $APPLICATION_DIRECTORY ******"
mv $DIR/services $APPLICATION_DIRECTORY/
mv $DIR/scripts $APPLICATION_DIRECTORY/

mv $CONFIG_FILE $APPLICATION_DIRECTORY/configs.json
echo "THE CONFIG FILE IS MOVED TO $APPLICATION_DIRECTORY"
CONFIG_FILE_P=$APPLICATION_DIRECTORY/configs.json
# create services
sudo chmod +x $APPLICATION_DIRECTORY/services/connector/connector.sh
sudo chmod +x $APPLICATION_DIRECTORY/services/consumer_manager/consumerManager.sh
sudo chmod +x $APPLICATION_DIRECTORY/services/events_app/ingest.py
sudo chmod +x $APPLICATION_DIRECTORY/services/risk_level_manager/orgapp.sh
sudo chmod +x $APPLICATION_DIRECTORY/services/user_app/userapp.sh

$APPLICATION_DIRECTORY/services/connector/connector.sh service -c $CONFIG_FILE_P
$APPLICATION_DIRECTORY/services/consumer_manager/consumerManager.sh service -c $CONFIG_FILE_P
$APPLICATION_DIRECTORY/services/events_app/ingest.py service -c $CONFIG_FILE_P
$APPLICATION_DIRECTORY/services/risk_level_manager/orgapp.sh service -c $CONFIG_FILE_P
$APPLICATION_DIRECTORY/services/user_app/userapp.sh service -c $CONFIG_FILE_P

sudo chmod +x $APPLICATION_DIRECTORY/scripts/*

#enable all services
echo "Enable all services....."
sudo systemctl enable okta_connector.service
sudo systemctl enable okta_consumer_manager.service
sudo systemctl enable okta_event.service
sudo systemctl enable okta_risk_level_manager.service
sudo systemctl enable okta_user.service
