#!/bin/bash

#####################################################################################################
#### Section One: Secrets for now stored outside the application path, and imported at runtime.
####              Later, these will come from a key vault.
#####################################################################################################

########################################################################
##### SECURITY ALERT: RE-WRITE THE FOLLOWING TO RETRIEVE THE SECRETS FROM A KEYVAULT OR FROM SOME SECURE LOCATION INSTEAD OF HARD CODING THEM HERE.

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

#Set AZURE_DEVOPS_EXT_PAT environment variable.  Used by az devops cli extension.  Keeping this separate from $AZ_PAT to increase customizability.  
export AZURE_DEVOPS_EXT_PAT=
echo 'export AZURE_DEVOPS_EXT_PAT=' >> /etc/environment
echo 'export AZURE_DEVOPS_EXT_PAT=' >> /etc/bashrc
echo 'export AZURE_DEVOPS_EXT_PAT=' >> /etc/profile

###########################################################################################################
#### Section Two:  wget the following block from a raw github url from this same repo.
###########################################################################################################


#MOST OF BELOW THIS CAN BE BAKED INTO AN IMAGE THAT WILL BE CHECKED OUT AT THE BEGINNING OF THIS DEPLOYMENT.
#THAT WAY, THIS DEPLOYMENT CAN THEN JUST HAVE A FEW LINES OF SCRIPT/FUNCTION CALLS HERE SO THAT THIS FILE CAN MAINLY BE SECRETS INPORTATION UNTIL THESE SECRETS ARE IN A KEY VAULT.

echo "About to check if azureuser exists.  1 if exists and 0 if does not exist: "
grep -c '^azureuser:' /etc/passwd

#Configure user to not require password to execute sudo commands by first deleting sudoer membership and then recreating without password requirement.
rm -f /etc/sudoers.d/waagent

cat << 'EOF' > /etc/sudoers.d/waagent
azureuser ALL=(ALL) NOPASSWD: ALL
EOF

## Install dependencies:  
yum update -y
yum install -y git openssl curl dos2unix

## Install Terraform
cd /home/azureuser
mkdir terraform-download
cd terraform-download
wget https://releases.hashicorp.com/terraform/0.12.24/terraform_0.12.24_linux_amd64.zip
unzip terraform_0.12.24_linux_amd64.zip
#Move the terraform binary into a folder that is listed as part of the PATH variable.  
mv terraform /usr/local/bin/
cd /home/azureuser


echo "About to install python3"
yum install -y python3
yum install -y python3-setuptools
easy_install-3.7 pip


##Install the Azure CLI using the following 3 steps:  
rpm --import https://packages.microsoft.com/keys/microsoft.asc

sh -c 'echo -e "[azure-cli]
name=Azure CLI
baseurl=https://packages.microsoft.com/yumrepos/azure-cli
enabled=1
gpgcheck=1
gpgkey=https://packages.microsoft.com/keys/microsoft.asc" > /etc/yum.repos.d/azure-cli.repo'

yum install -y azure-cli

#Install Powershell in the following steps:
mkdir /home/azureuser/powershell-download
cd /home/azureuser/powershell-download
sudo yum install -y wget
wget https://github.com/PowerShell/PowerShell/releases/download/v7.0.1/powershell-7.0.1-1.rhel.7.x86_64.rpm
sudo yum install -y powershell-7.0.1-1.rhel.7.x86_64.rpm
#You should now be able to open powershell by typing "pwsh" in the command line

cd /home/azureuser
## Download the agent to the VM:  
ls -al
mkdir agent-download
cd agent-download
#Old agent commented out June 8 2020
#wget https://vstsagentpackage.azureedge.net/agent/2.166.4/vsts-agent-linux-x64-2.166.4.tar.gz
#tar xvf vsts-agent-linux-x64-2.166.4.tar.gz
#New agent replacement June 8 2020 as follows in next 2 lines:
wget https://vstsagentpackage.azureedge.net/agent/2.169.1/vsts-agent-linux-x64-2.169.1.tar.gz
tar xvf vsts-agent-linux-x64-2.169.1.tar.gz

chown -R azureuser:azureuser /home/azureuser/terraform-download
chown -R azureuser:azureuser /home/azureuser/agent-download
chown -R azureuser:azureuser /home/azureuser


###############################################################################################
#### Section Three: wget this from raw github url in same repo.
###############################################################################################

##Install the agent as a systemd service using the following 8 commands, which depend on the environment variables you just set in the line above this line.  
echo "About to switch to azureuser, then run many install commands.  "
su - azureuser << EOF
#### su - azureuser
echo "User from whoami is: "
whoami
echo "The client is: $AZ_CLIENT "
echo "About to login to az.  "
az login --service-principal -u $AZ_CLIENT -p $AZ_PASS --tenant $AZ_TENANT
echo "About to cd into agent-download directory.  "
cd /home/azureuser/agent-download/
echo "User from whoami is: "
whoami
echo "The server is: $AZ_SERVER "
echo "About to run the config sh script.  "
./config.sh --unattended --url $AZ_SERVER --auth pat --token $AZ_PAT --pool default --agent rhelBox --replace --acceptTeeEula
echo "About to run the install dependencies sh script.  "
sudo ./bin/installdependencies.sh
#Wait for the svc.sh file to be created before running it in subsequent steps.
echo "About to begin sleeping until the svc sh script has been found.  "
while [ ! -f /home/azureuser/agent-download/svc.sh ]; do sleep 1; done
echo "Finished sleeping because the svc sh file has now been found.  "
sudo ./svc.sh install
sudo ./svc.sh start
sudo ./svc.sh status
EOF


echo "About to enable python3 to be called by the python command "
rm /usr/bin/python
ln -s /usr/bin/python3 /usr/bin/python

