#!/bin/bash

#####################################################################################################
#### Set the environment variables on the machine from which the terraform code to create the 
#### agile cloud manager will be run.  These will enable the Terraform azurerm provider to use 
#### the az cli upon which it is built.  These vars will need to be populated before using this file.
#####################################################################################################

echo "About to set environment_variables .  "

#Set AZ_PASS environment variable:
export AZ_PASS=
echo 'export AZ_PASS=' >> /etc/environment
echo 'export AZ_PASS=' >> /etc/bashrc
echo 'export AZ_PASS=' >> /etc/profile

#Set AZ_CLIENT environment variable:
export AZ_CLIENT=
echo 'export AZ_CLIENT=' >> /etc/environment
echo 'export AZ_CLIENT=' >> /etc/bashrc
echo 'export AZ_CLIENT=' >> /etc/profile

#Set AZ_TENANT environment variable:
export AZ_TENANT=
echo 'export AZ_TENANT=' >> /etc/environment
echo 'export AZ_TENANT=' >> /etc/bashrc
echo 'export AZ_TENANT=' >> /etc/profile

#Set AZ_PAT environment variable: 
export AZ_PAT=
echo 'export AZ_PAT=' >> /etc/environment
echo 'export AZ_PAT=' >> /etc/bashrc
echo 'export AZ_PAT=' >> /etc/profile

#Set AZ_SERVER environment variable:  
export AZ_SERVER=
echo 'export AZ_SERVER=' >> /etc/environment
echo 'export AZ_SERVER=' >> /etc/bashrc
echo 'export AZ_SERVER=' >> /etc/profile
