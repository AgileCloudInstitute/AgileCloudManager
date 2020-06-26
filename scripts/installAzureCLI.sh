#!/bin/bash

#Get the microsoft key 
sudo rpm --import https://packages.microsoft.com/keys/microsoft.asc

#Set the local yum pointer to the official microsoft repo for azure-cli
sudo sh -c 'echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo'

#Workaround a bug in the az-cli installation that fails to see that Python 3.6+ is already installed.
#Identify the most recent version of the RPM from this address: https://packages.microsoft.com/yumrepos/azure-cli/
#Then specify the RPM explicitly in the following line:
sudo rpm -ivh --nodeps azure-cli-2.8.0-1.el7.x86_64.rpm

#Install the azure-devops extension of the az-cli
az extension add --name azure-devops
