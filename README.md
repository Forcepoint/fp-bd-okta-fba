# okta POC
## Table of contents
* [General info](#general-info)
* [Technologies](#technologies)
* [Setup](#setup)

## General info
Forcepoint FBA ingests Okta auth data.
all the scripts in this project are used only for POC purpose.

installer.sh script installs all services on CentOS machine

## Technologies
* Python Required version is 3 and above
* Python module 'requests' is required
* Python module 'flask' is required
* Python module 'confluent_kafka' is required

## Setup
* Copy the installer.tar file into /root folder of the CentOS machine that will host it 
* Decompress the installer.tar file using the command 
```
tar -zxvf installer.tar 
```
* Go into the /root/installer folder and edit the configs.json file so that the parameters match the ones of your
current setup of Forcepoint Behavioral Analytics and Okta
* Make sure the installer.sh file is executable using the command 
```
sudo +x installer.sh
```
Install the Risk Level Manager using the command 
```
sudo ./installer.sh 
```
The installer script will read the configs.json file, move the services to application_directory and create
all services. The config file will then be moved to application_directory(defined in configs.json), do not change the location of this file. 
* Once the installation is completed, reboot the CentOS machine
* After reboot is completed, log into the CentOS machine and verify all 5 services of the Risk Level Manager are
running with the command systemctl list-units | grep okta
the status of all services must be 'loaded active running'
 